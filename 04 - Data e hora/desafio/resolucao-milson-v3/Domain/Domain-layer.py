class Cliente:
    def __init__(self, nome, endereco, cpf, data_nascimento):
        self.nome = nome
        self.endereco = endereco
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.contas = []
        
    def adicionar_conta(self, conta):
        self.contas.append(conta)
        
    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= 2:
            raise Exception("Excedeu o número de transações diárias.")
        transacao.registrar(conta)


class Conta:
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.saldo = 0
        self.historico = Historico()

    def depositar(self, valor):
        if valor <= 0:
            raise ValueError("Valor do depósito deve ser positivo.")
        self.saldo += valor
        print("Depósito realizado com sucesso!")

    def sacar(self, valor):
        if valor <= 0:
            raise ValueError("Valor do saque deve ser positivo.")
        if valor > self.saldo:
            raise Exception("Saldo insuficiente.")
        self.saldo -= valor
        print("Saque realizado com sucesso!")
        

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        if len([t for t in self.historico.transacoes if t["tipo"] == "Saque"]) >= self.limite_saques:
            raise Exception("Número máximo de saques excedido.")
        if valor > self.limite:
            raise Exception("Valor excede o limite de saque.")
        super().sacar(valor)
