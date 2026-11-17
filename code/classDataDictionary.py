import datetime
import re

class DataDictionary:
    
    def __init__(self, filePathDb = "../txtFiles/passwords.txt", 
                filePathStrengthValidation = "../txtFiles/passwordsStrengthValidation.txt", 
                filePathLogs = "../txtFiles/logs.txt",
                filePathPasswordNotUsable = "../txtFiles/passwordsNotUsable.txt"):
            
        self.filePathDb = filePathDb
        self.filePathStrengthValidation = filePathStrengthValidation
        self.filePathLogs = filePathLogs
        self.filePathPasswordNotUsable = filePathPasswordNotUsable


    def writeFunctions(self,path, text, type):
        try:
            file = open(path, type)
            file.write(text)
            file.close()
        except Exception as e:
            print(e)

    def defaultDictionaryFromTxt(self, uneditedArchive):
        arrResult = []
        for i in uneditedArchive:
            i = i.replace("\n", "")
            if i.strip() == "":
                continue
            arrIndividualVal = i.split(",")
            arrResult.append({val.split(":")[0].strip(): val.split(":")[1].strip() for val in arrIndividualVal})
        return arrResult
    
    
    def getPasswordsDb(self):
        uneditedArchive = open(self.filePathDb, "r", encoding="utf8")
        archiveByLine = uneditedArchive.readlines()
        uneditedArchive.close()
        return self.defaultDictionaryFromTxt(archiveByLine)
    
    def revealPassword(self, searchCriteria):
        allCredentials = self.getPasswordsDb()
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas."}

        for credential in allCredentials:
            is_match = (
                credential.get("servicename", "").strip().lower() == searchCriteria["servicename"].strip().lower() and
                credential.get("usuario", "").strip() == searchCriteria["usuario"].strip()
            )
            
            if is_match:
                self.log_operation("Revelar Senha", credential.get("servicename"))
                return {
                    "code": 200, 
                    "message": f"Senha revelada com sucesso!", 
                    "senha": credential.get("senha")
                }

        return {"code": 404, "message": "Credencial não encontrada para revelar a senha."}
    
    def getStrengthValidationDb(self):
        uneditedArchive = open(self.filePathStrengthValidation, "r", encoding="utf8")
        archiveByLine = uneditedArchive.readlines()
        uneditedArchive.close()
        return self.defaultDictionaryFromTxt(archiveByLine)
    
    def getPasswordNotUsableDb(self):
        uneditedArchive = open(self.filePathPasswordNotUsable, "r", encoding="utf8")
        archiveByLine = uneditedArchive.readlines()
        uneditedArchive.close()
        return self.defaultDictionaryFromTxt(archiveByLine)
    
    def generateUniqueId(self):
        passwordDb = self.getPasswordsDb()
        higherId = 0

        for credential in passwordDb:
            currentId = int(credential["id"])
            if currentId > higherId:
                higherId = currentId

        return higherId + 1
    
    def hideValueForDisplay(self, value):
        if len(value) <= 2:
            return "*" * len(value)
        else:
            return value[0] + "*" * (len(value) - 2) + value[-1]
    
    def evaluatePasswordStrength(self, password):
        min_8 = len(password) >= 8
        min_12 = len(password) >= 12
        has_upper = re.search(r"[A-Z]", password) is not None
        has_lower = re.search(r"[a-z]", password) is not None
        has_num = re.search(r"[0-9]", password) is not None
        has_special = re.search(r"[^A-Za-z0-9]", password) is not None
        score = sum([min_8, min_12, has_upper, has_lower, has_num, has_special])
        if score <= 3:
            strength = "Fraca"
        elif score <= 5:
            strength = "Media"
        else:
            strength = "Forte"
        return {
            "strength": strength,
            "minLength8": min_8,
            "minLength12": min_12,
            "hasUpperCase": has_upper,
            "hasLowerCase": has_lower,
            "hasNumbers": has_num,
            "hasSpecialChars": has_special
        }

    def strengthNecessaryForPassword(self, category):
        categories = self.getStrengthValidationDb()
        for cat in categories:
            if cat["categoryName"].lower() == category.lower():
                return cat["categoryStrength"].lower()
        return "forte"

            
    
    def isAValidPassword(self, password, category):
        passwordNotUsableDb = self.getPasswordNotUsableDb()
        for entry in passwordNotUsableDb:
            if entry["senha"] == password:
                return {"code": 400, "message": "Senha não é válida. Ela está na lista de senhas não utilizáveis."}
        numericalStrength = {"fraca": 1, "media": 2, "forte": 3}
        strengthRequired = self.strengthNecessaryForPassword(category)
        min_strength = numericalStrength.get(strengthRequired)
        passwordStrength = self.evaluatePasswordStrength(password)
        passwordStrengthNumber = numericalStrength.get(passwordStrength["strength"].lower())

        if passwordStrengthNumber >= min_strength:
            return {"code": 200, "message": "Senha é válida."}
        
        mensagens_pendencia = {
            "minLength8": "ter pelo menos 8 caracteres",
            "minLength12": "ter pelo menos 12 caracteres",
            "hasUpperCase": "conter letras maiúsculas (A-Z)",
            "hasLowerCase": "conter letras minúsculas (a-z)",
            "hasNumbers": "conter números (0-9)",
            "hasSpecialChars": "conter caracteres especiais (ex: @, #, $)"
        }
        
        falhas = []
        for key, isClear in passwordStrength.items():
            if key != "strength" and not isClear:
                if key in mensagens_pendencia:
                    falhas.append(mensagens_pendencia[key])
        
        detalhes = ", ".join(falhas)
        mensagem_erro = f"Senha não é válida. Força atual: {passwordStrength['strength']} (Mínimo exigido: {strengthRequired.capitalize()}). Para melhorar, você precisa: {detalhes}."
        
        return {"code": 400, "message": mensagem_erro}
    
    def createCredencials(self, dicUserInput):
        uniqueId = self.generateUniqueId()
        dicUserInput = {
        "id": uniqueId,
        **dicUserInput
        }
        passwordStrength = self.isAValidPassword(dicUserInput["senha"], dicUserInput["servicename"])
        if passwordStrength["code"] != 200:
            return {"code": passwordStrength["code"], "message": passwordStrength["message"]}

        credentialString = ",".join(
        f"{key}: {value}" for key, value in dicUserInput.items()
        ) + "\n"
        self.writeFunctions(self.filePathDb, credentialString, "a")
        self.log_operation("Cadastrar Credencial", dicUserInput["servicename"], uniqueId)
        return {"code": 200, "message": "Credenciais criadas com sucesso!"}
    
    def listCredentials(self, searchBy, searchData):
        searchBy = searchBy.strip().lower()
        allCredentials = self.getPasswordsDb()
        if searchBy == "senha":
            return ({"code" : 404}, [])
        if not allCredentials:
            return ({"code" : 201}, [])
        if searchBy != "" and searchBy not in allCredentials[0]:
            return ({"code" : 401}, [])
        
        foundCredentials = []
        if searchBy == "" and searchData == "":
            for credential in allCredentials:
                cred_copy = credential.copy()
                if "senha" in cred_copy:
                    hiddenPassword = self.hideValueForDisplay(cred_copy["senha"])
                    cred_copy["senha"] = hiddenPassword
                foundCredentials.append(cred_copy)
            return ({"code" : 200}, foundCredentials)
        
        for credential in allCredentials:
            if searchBy in credential:
                dbValue = str(credential[searchBy])
                if searchData.lower() in dbValue.lower():
                    cred_copy = credential.copy()
                    if "senha" in cred_copy:
                        hiddenPassword = self.hideValueForDisplay(cred_copy["senha"])
                        cred_copy["senha"] = hiddenPassword
                    foundCredentials.append(cred_copy)

        return ({"code" : 200}, foundCredentials)
    
    def deleteCredentials(self, searchCriteria):
        allCredentials = self.getPasswordsDb()
        
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas."}

        found = False
        deletedId = None
        updatedCredentials = []

        for credential in allCredentials:
            is_match = (
                credential.get("servicename", "").strip().lower() == searchCriteria["servicename"].strip().lower() and
                credential.get("usuario", "").strip() == searchCriteria["usuario"].strip() and
                credential.get("senha", "").strip() == searchCriteria["senha"].strip()
            )
            
            if is_match:
                found = True 
                deletedId = credential.get("id")
            else:
                updatedCredentials.append(credential)

        if not found:
            return {"code": 404, "message": "Credencial não encontrada. Verifique se o serviço, usuário e senha atuais estão corretos."}

        allDataString = ""
        for cred in updatedCredentials:
            credentialString = ",".join(
                f"{key}: {val}" for key, val in cred.items()
            ) + "\n"
            allDataString += credentialString
        try:
            self.writeFunctions(self.filePathDb, allDataString, "w")
            self.log_operation("Deletar Credencial", searchCriteria["servicename"], deletedId)
            return {"code": 200, "message": "Credencial deletada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao atualizar o arquivo após deleção: {e}"}
    
    def updateCredentials(self, searchCriteria, newValues):
        allCredentials = self.getPasswordsDb()
        
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas."}

        found = False
        credId = None
        for credential in allCredentials:
            if (credential.get("servicename", "").strip().lower() == searchCriteria["servicename"].strip().lower() and
                credential.get("usuario", "").strip() == searchCriteria["usuario"].strip() and
                credential.get("senha", "").strip() == searchCriteria["senha"].strip()):
                
                found = True
                credId = credential.get("id")
                for key, value in newValues.items():
                    if value is not None:
                        if key == "senha":
                            passwordStrength = self.isAValidPassword(value, credential.get("servicename", ""))
                            if passwordStrength["code"] != 200:
                                return {"code": passwordStrength["code"], "message": passwordStrength["message"]}
                        credential[key] = value
                break

        if not found:
            return {"code": 404, "message": "Credencial não encontrada. Verifique se o serviço, usuário e senha atuais estão corretos."}

        allDataString = ""
        for cred in allCredentials:
            credentialString = ",".join(
                f"{key}: {val}" for key, val in cred.items()
            ) + "\n"
            allDataString += credentialString
        try:
            self.writeFunctions(self.filePathDb, allDataString, "w")
            self.log_operation("Atualizar Credencial", searchCriteria["servicename"], credId)
            return {"code": 200, "message": "Credencial atualizada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao salvar alterações no arquivo: {e}"}
    
    def createCategory(self, categoryData):
        categoryName = categoryData["categoryName"]
        categoryStrength = categoryData["categoryStrength"]
        getStrengthValidationDb = self.getStrengthValidationDb()

        if not categoryName or not categoryStrength:
            return {"code": 400, "message": "Nome da categoria e força mínima são obrigatórios."}
        
        if categoryStrength not in ["fraca", "media", "forte"]:
            return {"code": 400, "message": "Força mínima inválida. Use 'fraca', 'media' ou 'forte'."}
        
        if any(category["categoryName"].lower() == categoryName.lower() for category in getStrengthValidationDb):
            return {"code": 409, "message": "Categoria já existe."}

        newCategoryString = f"categoryName: {categoryName}, categoryStrength: {categoryStrength}\n"
        
        try:
            self.writeFunctions(self.filePathStrengthValidation, newCategoryString, "a")
            return {"code": 200, "message": "Categoria criada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao salvar a nova categoria: {e}"}
        
    def listCategories(self, searchByCateg):
        allCategories = self.getStrengthValidationDb()
        
        if not allCategories:
            return {"code": 201,
                    "message": "Não há categorias cadastradas.",
                    "categories": []}
        
        if searchByCateg:
            foundCategories = [category for category in allCategories if searchByCateg.lower() in category["categoryName"].lower()]
            if not foundCategories:
                return {"code": 404, "message": "Categoria não encontrada."}
            
            return {"code": 200,
                    "message": "Categorias encontradas.",
                    "categories": foundCategories}

        return {"code": 200,
                "message": "Todas as categorias.",
                "categories": allCategories}
    
    def editCategory(self, editCategoryData):
        categoryName = editCategoryData["categoryName"]
        newCategoryStrength = editCategoryData["newCategoryStrength"]
        allCategories = self.getStrengthValidationDb()

        if not allCategories:
            return {"code": 201, "message": "Não há categorias cadastradas."}

        if newCategoryStrength not in ["fraca", "media", "forte"]:
            return {"code": 400, "message": "Força mínima inválida. Use 'fraca', 'media' ou 'forte'."}
        
        found = False
        for category in allCategories:
            if category["categoryName"].lower() == categoryName.lower():
                found = True
                if newCategoryStrength:
                    category["categoryStrength"] = newCategoryStrength
                break

        if not found:
            return {"code": 404, "message": "Categoria não encontrada."}

        allDataString = ""
        for cat in allCategories:
            categoryString = f"categoryName: {cat['categoryName']}, categoryStrength: {cat['categoryStrength']}\n"
            allDataString += categoryString

        try:
            self.writeFunctions(self.filePathStrengthValidation, allDataString, "w")
            return {"code": 200, "message": "Categoria atualizada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao salvar alterações no arquivo: {e}"}

    def deleteCategory(self, deleteCategoryData):
        categoryName = deleteCategoryData["categoryName"]
        allCategories = self.getStrengthValidationDb()

        if not allCategories:
            return {"code": 201, "message": "Não há categorias cadastradas."}

        found = False
        updatedCategories = []

        for category in allCategories:
            if category["categoryName"].lower() == categoryName.lower():
                found = True
            else:
                updatedCategories.append(category)

        if not found:
            return {"code": 404, "message": "Categoria não encontrada."}

        allDataString = ""
        for cat in updatedCategories:
            categoryString = f"categoryName: {cat['categoryName']}, categoryStrength: {cat['categoryStrength']}\n"
            allDataString += categoryString

        try:
            self.writeFunctions(self.filePathStrengthValidation, allDataString, "w")
            return {"code": 200, "message": "Categoria deletada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao salvar alterações no arquivo: {e}"}
        
    def validateRepeatedPasswords(self):
        allCredentials = self.getPasswordsDb()
        if not allCredentials:
            return {"code": 204, "message": "Não há credenciais cadastradas."}

        passwordMap = {}

        for credential in allCredentials:
            password = credential.get("senha")
            if password:
                if password not in passwordMap:
                    passwordMap[password] = []
                passwordMap[password].append(credential)

        repeatedDetails = []

        for password, creds in passwordMap.items():
            if len(creds) > 1:
                hidden_password = self.hideValueForDisplay(password)
                
                # Lista formatada com os serviços e emails afetados
                affected_services = [
                    {
                        "servicename": c.get("servicename"),
                        "email": c.get("email"),
                        "usuario": c.get("usuario")
                    } for c in creds
                ]
                
                repeatedDetails.append({
                    "senha": hidden_password,
                    "vinculos": affected_services
                })

        if repeatedDetails:
            return {"code": 200, "repeatedPasswords": repeatedDetails}
        else:
            return {"code": 204, "message": "Não há senhas repetidas."}
        
    def log_operation(self, operation, servicename="N/A", credential_id="N/A"):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"datetime: {current_time}, operation: {operation}, id: {credential_id}, servicename: {servicename}\n"
        
        try:
            self.writeFunctions(self.filePathLogs, log_entry, "a")
        except Exception as e:
            print(f"Erro ao escrever no log: {e}")
            
    def revealPasswordById(self, credentialIds):
        allCredentials = self.getPasswordsDb()
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas."}

        found_credentials = []
        notFoundIds = []

        credentials_map = {str(cred.get("id")): cred for cred in allCredentials if cred.get("id") is not None}

        for target_id in credentialIds:
            if target_id in credentials_map:
                credential = credentials_map[target_id]
                service_name = credential.get("servicename", "N/A")
                cred_id = credential.get("id", "N/A")
                
                self.log_operation("Revelar Senha", service_name, cred_id)
                
                found_credentials.append({
                    "id": cred_id,
                    "servicename": service_name,
                    "senha": credential.get("senha")
                })
            else:
                notFoundIds.append(target_id)

        if found_credentials:
            return {
                "code": 200,
                "message": "Senhas reveladas com sucesso!",
                "credentials": found_credentials,
                "notFoundIds": notFoundIds
            }

        return {"code": 404, "message": "Nenhum dos IDs informados foi encontrado."}
    
    def getLogs(self):
        try:
            with open(self.filePathLogs, "r", encoding="utf8") as file:
                logs_lines = file.readlines()
                
            if not logs_lines:
                return {"code": 201, "message": "O arquivo de log está vazio."}
                
            cleaned_logs = [line.strip() for line in logs_lines if line.strip()]
            return {"code": 200, "logs": cleaned_logs}
            
        except FileNotFoundError:
            return {"code": 404, "message": "Arquivo de log ainda não foi criado (nenhuma operação registrada)."}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao ler o arquivo de log: {e}"}
    
    def getUserSecuritySummary(self):
        allCredentials = self.getPasswordsDb()
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas para gerar o resumo."}

        totalCredentials = len(allCredentials)
        weakPasswordsCount = 0
        commonPasswordsCount = 0

        notUsableDb = self.getPasswordNotUsableDb()
        notUsableSet = {entry.get("senha") for entry in notUsableDb}

        passwordCounts = {}
        for cred in allCredentials:
            pwd = cred.get("senha")
            if pwd:
                passwordCounts[pwd] = passwordCounts.get(pwd, 0) + 1

        credentialsSummary = []
        now = datetime.datetime.now()

        for cred in allCredentials:
            pwd = cred.get("senha", "")
            service = cred.get("servicename", "Desconhecido")
            user = cred.get("usuario", "Desconhecido")
            credId = cred.get("id", "N/A")
            
            strengthData = self.evaluatePasswordStrength(pwd)
            isWeak = strengthData["strength"].lower() == "fraca"
            if isWeak:
                weakPasswordsCount += 1

            isCommon = pwd in notUsableSet
            if isCommon:
                commonPasswordsCount += 1

            isRepeated = passwordCounts.get(pwd, 0) > 1

            dateStr = cred.get("datetime")
            timeUnchanged = "Data não registrada"
            if dateStr:
                try:
                    if isinstance(dateStr, str):
                        formatedDateCred = datetime.datetime.fromisoformat(dateStr.strip())
                    else:
                        formatedDateCred = dateStr

                    delta = now - formatedDateCred
                    days = delta.days
                    if days == 0:
                        timeUnchanged = "Alterada hoje"
                    else:
                        timeUnchanged = f"Há {days} dias"
                except Exception:
                    timeUnchanged = str(dateStr)

            credentialsSummary.append({
                "id": credId,
                "servicename": service,
                "usuario": user,
                "strength": strengthData["strength"],
                "isWeak": isWeak,
                "isCommon": isCommon,
                "isRepeated": isRepeated,
                "timeUnchanged": timeUnchanged
            })

        repeatedTotalCount = sum(1 for pwd, count in passwordCounts.items() if count > 1)

        return {
            "code": 200,
            "totalCredentials": totalCredentials,
            "weakPasswordsCount": weakPasswordsCount,
            "commonPasswordsCount": commonPasswordsCount,
            "repeatedPasswordsCount": repeatedTotalCount,
            "details": credentialsSummary
        }