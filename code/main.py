from classDataDictionary import DataDictionary
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
        for data in dataToDisplay:
            print(data)

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
    print("9 - Sair do programa\n")


    try:
        opCode = int(input())
        if opCode == 9:
            runningCode = False
        elif opCode > 8 or opCode < 1:
            print("\n Codigo nao configurado favor escolher um codigo valido")
        else:
            dataDictionary =  DataDictionary()
            match opCode:
                case 1:
                    payloadMessage =dataDictionary.createCredencials(getUserInputForCreate())
                    print(f"\n{payloadMessage['message']}")
                case 2:
                    searchBy, searchValue = getUserInputForSelect()
                    displayDataFromSelect(*dataDictionary.listCredentials(searchBy, searchValue))
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
    except Exception as e:
        print(e)
