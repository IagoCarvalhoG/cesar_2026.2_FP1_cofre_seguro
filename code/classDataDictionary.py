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
            arrIndividualVal = i.split(",")
            arrResult.append({val.split(":")[0].strip(): val.split(":")[1].strip() for val in arrIndividualVal})
        return arrResult
    
    def getPasswordsDb(self):
        uneditedArchive = open(self.filePathDb, "r", encoding="utf8")
        archiveByLine = uneditedArchive.readlines()
        uneditedArchive.close()
        return self.defaultDictionaryFromTxt(archiveByLine)
    
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
        
        # Monta a mensagem descritiva com o que falta
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
        updatedCredentials = []

        for credential in allCredentials:
            is_match = (
                credential.get("servicename", "").strip().lower() == searchCriteria["servicename"].strip().lower() and
                credential.get("usuario", "").strip() == searchCriteria["usuario"].strip() and
                credential.get("senha", "").strip() == searchCriteria["senha"].strip()
            )
            
            if is_match:
                found = True 
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
            return {"code": 200, "message": "Credencial deletada com sucesso!"}
        except Exception as e:
            return {"code": 500, "message": f"Erro ao atualizar o arquivo após deleção: {e}"}
    
    def updateCredentials(self, searchCriteria, newValues):
        allCredentials = self.getPasswordsDb()
        
        if not allCredentials:
            return {"code": 201, "message": "Não há credenciais cadastradas."}

        found = False

        for credential in allCredentials:
            if (credential.get("servicename", "").strip().lower() == searchCriteria["servicename"].strip().lower() and
                credential.get("usuario", "").strip() == searchCriteria["usuario"].strip() and
                credential.get("senha", "").strip() == searchCriteria["senha"].strip()):
                
                found = True
                
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