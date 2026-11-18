from classDataDictionary import DataDictionary
from agente import falar_com_agente_texto
import datetime


def getUserInputForCreate():
    serviceName = str(input("Inserir nome do serviço\n")).strip().lower()
    usuario = str(input("Inserir nome de usuario\n")).strip()
    email = str(input("Inserir email\n")).strip()
    senha = str(input("Inserir senha\n")).strip()
    observacoes = str(input("Inserir observacoes\n")).strip()
    dateTime = datetime.datetime.now()
    return {"servicename": serviceName,
            "usuario":usuario,
            "email" : email, 
            "senha" : senha, 
            "observacoes" : observacoes, 
            "datetime" : dateTime  }

def getUserInputForSelect():
    searchBy = str(input("Inserir tipo de dado a usar na busca\n")).strip().lower()
    searchValue = str(input("Inserir valor a ser buscado\n")).strip()
    return(searchBy, searchValue)

def displayDataFromSelect(code, dataToDisplay):
    if code["code"] == 404:
        print("Busca nao pode ser feita pelo campo senha")
    elif code["code"] == 201:
        print("Nao existe nenhum dado cadastrado ainda")
    elif code["code"] == 401:
        print("Credential nao encontrada para o tipo da busca e valor usado")
    else:
        print("-" * 60)
        for data in dataToDisplay:
            print(f"\nID: {data.get('id')} | Serviço: {data.get('servicename').capitalize()}")
            print(f"\n  - Usuário: {data.get('usuario')}")
            print(f"\n  - Email: {data.get('email')}")
            print(f"\n  - Senha: {data.get('senha')}")
            print(f"\n  - Observações: {data.get('observacoes')}")
            print("-" * 60)

def getUserInputForUpdate():
    valService = input("Digite o nome do serviço atual: \n").strip()
    valUsuario = input("Digite o nome de usuário atual: \n").strip()
    valSenha = input("Digite a senha atual: \n").strip()
    
    newService = input("Novo nome do serviço: \n").strip()
    newUsuario = input("Novo nome de usuário: \n").strip()
    newEmail = input("Novo email: \n").strip()
    newSenha = input("Nova senha: \n").strip()
    newObs = input("Novas observações: \n").strip()
    dateTime = datetime.datetime.now()
    searchCriteria = {
        "servicename": valService,
        "usuario": valUsuario,
        "senha": valSenha
    }
    
    newValues = {
        "servicename": newService if newService else None,
        "usuario": newUsuario if newUsuario else None,
        "email": newEmail if newEmail else None,
        "senha": newSenha if newSenha else None,
        "observacoes": newObs if newObs else None,
        "datetime": dateTime 
    }
    
    return searchCriteria, newValues

def getUserInputForDelete():
    service = input("Digite o nome do serviço da credencial que deseja apagar: \n").strip()
    user = input("Digite o nome de usuário: \n").strip()
    password = input("Digite a senha: \n").strip()
    
    return {
        "servicename": service,
        "usuario": user,
        "senha": password
    }

def getUserInputForCreateCategory():
    categoryName = input("Digite a categoria a ser cadastrada: \n").strip().lower()
    categoryStrength = input("Digite a força de senha mínima para essa categoria (fraca, media, forte): \n").strip().lower()
    return {
        "categoryName": categoryName,
        "categoryStrength": categoryStrength
    }

def getUserInputForListCategories():
    searchByCateg = str(input("Inserir categoria a ser buscada\n")).strip().lower()
    return searchByCateg

def getUserInputForEditCategory():
    categoryName = input("Digite a categoria que deseja editar: \n").strip().lower()
    newCategoryStrength = input("Digite a nova força de senha mínima para essa categoria (fraca, media, forte)\n").strip().lower()
    
    return {
        "categoryName": categoryName,
        "newCategoryStrength": newCategoryStrength
    }
    
def getUserInputForDeleteCategory():
    categoryName = input("Digite a categoria que deseja apagar: \n").strip().lower()
    return {
        "categoryName": categoryName
    }
    
def repeatedPasswordValidation(dataDictionary):
    payload = dataDictionary.validateRepeatedPasswords()
    if payload["code"] == 200:
        print("\n Alerta: Senhas repetidas encontradas!")
        for item in payload["repeatedPasswords"]:
            print(f"\nSenha mascarada: {item['senha']}")
            print("\nUtilizada nos seguintes serviços:")
            for vinculo in item["vinculos"]:
                print(f"\n  - Serviço: {vinculo['servicename']} | Email/Usuário: {vinculo['email']}/{vinculo['usuario']}")
    elif payload["code"] == 204:
        print(f"\n{payload['message']}")
    
def warningsValidation(dataDictionary):
    repeatedPasswordValidation(dataDictionary)

def runAgentChatWithSecurity(dataDictionary):
    
    print("\n--------------------------------------------------")
    print("              Chamada ao agente de IA externo"       )
    print("--------------------------------------------------")

    try:
        allCredentials = dataDictionary.getPasswordsDb()
    except Exception as e:
        print(f"\n Erro ao ler o banco de dados de credenciais: {e}")
        return

    if not allCredentials:
        print(f"\n Não há credenciais cadastradas no sistema para o agente consultar.")
        return

    texto_dados = "id,servicename,usuario,email,observacoes,datetime\n"
    for cred in allCredentials:
        cId = cred.get("id", "")
        service = cred.get("servicename", "")
        user = cred.get("usuario", "")
        email = cred.get("email", "")
        obs = cred.get("observacoes", "")
        dt = cred.get("datetime", "")
        
        texto_dados += f"{cId},{service},{user},{email},{obs},{dt}\n"

    print("\n AVISO DE SEGURANÇA: Esta funcionalidade envia os metadados das suas credenciais")
    print("   (sem as senhas reais) para o modelo de Inteligência Artificial externo.")
    confirmation = input("Deseja prosseguir e conversar com o agente? (s/n): ").strip().lower()
    
    if confirmation != 's':
        print("\n Operação cancelada pelo usuário.")
        return

    print(f"\n Base de dados carregada com sucesso ({len(allCredentials)} registros).")
    print(" Digite 'sair' a qualquer momento para retornar ao menu principal.\n")

    while True:
        pergunta = input("Pergunta ao Agente > ").strip()
        if pergunta.lower() == "sair":
            print("\nEncerrando chat com o agente. Retornando ao menu principal...")
            break
        
        if not pergunta:
            continue

        print("\n--------------------------------------------------")
        
        try:
            dataDictionary.log_operation(
                operation="Consulta Agente de IA", 
                servicename="IA Assistant", 
                credential_id=f"Pergunta: {pergunta}"
            )

            falar_com_agente_texto(texto_dados, pergunta, "CofreSeguro")

        except Exception as e:
            print(f" Erro de conexão ou configuração com o Agente de IA: {e}")
            print("Verifique se a chave de API está definida no arquivo .env e se há conexão com a internet.")
        
        print("\n--------------------------------------------------")
        
#####################
#
#
# Main code
#
#
####################


runningCode = True
while runningCode:
    print("1 - Cadastrar senha\n")
    print("2 - Ler credenciais\n")
    print("3 - Atualizar informações\n")
    print("4 - Apagar informações\n")
    print("5 - Cadastrar categorias e seus parametros de força de senha\n")
    print("6 - Listar categorias e seus parametros de força de senha\n")
    print("7 - Editar categoria e seu parametro de força de senha\n")
    print("8 - Apagar categoria e seu parametro de força de senha\n")
    print("9 - Exibir histórico de logs\n")
    print("10 - Exibir resumo de segurança da conta\n")
    print("11 - Pergunte ao agente de IA\n")
    print("12 - Verificar senhas vazadas (Have I Been Pwned)\n")
    print("0 - Sair do programa\n")


    try:
        opCode = int(input())
        if opCode == 0:
            runningCode = False
        elif opCode > 12 or opCode < 0:
            print("\n Codigo nao configurado favor escolher um codigo valido")
        else:
            dataDictionary =  DataDictionary()
            warningsValidation(dataDictionary)
            match opCode:
                case 1:
                    payloadMessage =dataDictionary.createCredencials(getUserInputForCreate())
                    print(f"\n{payloadMessage['message']}")
                case 2:
                    searchBy, searchValue = getUserInputForSelect()
                    code_result, credentials_list = dataDictionary.listCredentials(searchBy, searchValue)
                    displayDataFromSelect(code_result, credentials_list)
                    
                    if code_result.get("code") == 200 and credentials_list:
                        print("\n--------------------------------------------------")
                        try:
                            escolha_menu = int(input("\n1 - Revelar TODAS as senhas listadas acima\n2 - Voltar ao inicio do programa\nEscolha uma opção: "))
                            
                            if escolha_menu == 1:
                                idsToReveal = [str(cred.get("id")) for cred in credentials_list if "id" in cred]
                                revealPayload = dataDictionary.revealPasswordById(idsToReveal)
                                
                                if revealPayload["code"] == 200:
                                    print("\n Senhas Reveladas:")
                                    for cred in revealPayload["credentials"]:
                                        print(f"  - ID: {cred['id']} | Serviço: {cred['servicename']} | Senha: {cred['senha']}")
                                    
                                    if revealPayload.get("notFoundIds"):
                                        print(f"\n IDs não encontrados: {', '.join(revealPayload['notFoundIds'])}")
                                else:
                                    print(f"\n {revealPayload['message']}\n")
                                
                        except ValueError:
                            print("\n Entrada inválida! Digite apenas números. Retornando ao menu principal.")
                    
                case 3:
                    searchCriteria, newValues = getUserInputForUpdate()
                    updateResult = dataDictionary.updateCredentials(searchCriteria, newValues)                    
                    print(f"\n{updateResult['message']}")
                case 4:
                    searchCriteria = getUserInputForDelete()
                    deleteResult = dataDictionary.deleteCredentials(searchCriteria)
                    print(f"\n{deleteResult['message']}")
                case 5:
                    messagePayload = dataDictionary.createCategory(getUserInputForCreateCategory())
                    print(f"\n{messagePayload['message']}")
                case 6:
                    searchByCateg = getUserInputForListCategories()
                    messagePayload = dataDictionary.listCategories(searchByCateg)
                    print(f"\n{messagePayload['message']}")
                    if "categories" in messagePayload:
                        for category in messagePayload["categories"]:
                            print(f" - {category['categoryName']}: {category['categoryStrength']}")
                case 7:
                    editCategoryData = getUserInputForEditCategory()
                    messagePayload = dataDictionary.editCategory(editCategoryData)
                    print(f"\n{messagePayload['message']}")
                    pass
                case 8:
                    deleteCategoryData = getUserInputForDeleteCategory()
                    messagePayload = dataDictionary.deleteCategory(deleteCategoryData)
                    print(f"\n{messagePayload['message']}")
                case 9:
                    payload_logs = dataDictionary.getLogs()
                    if payload_logs["code"] == 200:
                        print("\n--- HISTÓRICO DE LOGS ---")
                        for log in payload_logs["logs"]:
                            print(f"  - {log}")
                        print("-" * 30)
                    else:
                        print(f"\n{payload_logs['message']}")
                case 10: 
                    summary = dataDictionary.getUserSecuritySummary()
                    if summary["code"] == 200:
                        print("\n--------------------------------------------------")
                        print(" \nResumo de Segurança da Conta")
                        print("\n--------------------------------------------------")
                        print(f"\n Total de credenciais cadastradas: {summary['totalCredentials']}")
                        print(f"\n Senhas classificadas como 'Fracas': {summary['weakPasswordsCount']}")
                        print(f"\n Senhas na lista de comuns/proibidas: {summary['commonPasswordsCount']}")
                        print(f"\n Senhas repetidas (reutilizadas): {summary['repeatedPasswordsCount']}")
                        print("\n------------------------------------------------------")
                        print("\nDetalhamento por serviço:")
                        print("\n------------------------------------------------------")
                        for item in summary["details"]:
                            print(f"\n  - ID: {item['id']} | Serviço: {item['servicename'].capitalize()} ({item['usuario']})")
                            print(f"\n  - Força: {item['strength']} | Comum: {'Sim' if item['isCommon'] else 'Não'} | Repetida: {'Sim' if item['isRepeated'] else 'Não'}")
                            print(f"\n  - Tempo sem alteração: {item['timeUnchanged']}")
                        print("\n------------------------------------------------------")
                    else:
                        print(f"\n{summary['message']}")
                case 11:
                    runAgentChatWithSecurity(dataDictionary)
                case 12:
                    print("\nConsultando base de senhas vazadas (Have I Been Pwned)...")
                    payload = dataDictionary.checkLeakedPasswords()
                    
                    if payload["code"] == 200:
                        print("\n ALERTA DE SEGURANÇA: Senhas comprometidas encontradas!")
                        print("\n------------------------------------------------------")
                        for item in payload["leaked"]:
                            print(f"\n  - Serviço: {item['servicename'].capitalize()} ({item['usuario']})")
                            print(f"\n  - Apareceu em vazamentos públicos {item['pwnedCount']} vezes!")
                        print("\n------------------------------------------------------")
                        print("\nRecomendação: Altere essas senhas imediatamente!")
                    elif payload["code"] in [201, 204, 503]:
                        print(f"\n {payload['message']}")
                    else:
                        print(f"\n {payload['message']}")
    except Exception as e:
        print(e)
