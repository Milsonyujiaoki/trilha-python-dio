def main():
    service = BancoService()

    while True:
        opcao = menu()

        if opcao == "nu":
            cpf = input("CPF: ")
            nome = input("Nome: ")
            data_nascimento = input("Data de Nascimento: ")
            endereco = input("Endereço: ")
            service.criar_cliente(nome, cpf, data_nascimento, endereco)
            print("Cliente criado com sucesso!")
            
        elif opcao == "nc":
            cpf = input("CPF do cliente: ")
            cliente = service._buscar_cliente(cpf)
            numero_conta = len(service.contas) + 1
            service.criar_conta_corrente(cliente, numero_conta)
            print("Conta criada com sucesso!")
        
        elif opcao == "d":
            cpf = input("CPF: ")
            valor = float(input("Valor: "))
            service.depositar(cpf, valor)

        elif opcao == "s":
            cpf = input("CPF: ")
            valor = float(input("Valor: "))
            service.sacar(cpf, valor)
