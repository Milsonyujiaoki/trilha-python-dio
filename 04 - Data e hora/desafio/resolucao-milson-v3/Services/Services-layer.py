class BancoService:
    def __init__(self):
        self.clientes = []
        self.contas = []

    def criar_cliente(self, nome, cpf, data_nascimento, endereco):
        if self._cpf_ja_existe(cpf):
            raise ValueError("Cliente com esse CPF já existe.")
        cliente = PessoaFisica(nome, cpf, data_nascimento, endereco)
        self.clientes.append(cliente)
        return cliente

    def criar_conta_corrente(self, cliente, numero):
        conta = ContaCorrente(numero, cliente)
        cliente.adicionar_conta(conta)
        self.contas.append(conta)
        return conta

    def _cpf_ja_existe(self, cpf):
        return any(cliente.cpf == cpf for cliente in self.clientes)
    
    def depositar(self, cpf, valor):
        cliente = self._buscar_cliente(cpf)
        conta = escolher_conta(cliente)
        conta.depositar(valor)
    
    def sacar(self, cpf, valor):
        cliente = self._buscar_cliente(cpf)
        conta = escolher_conta(cliente)
        conta.sacar(valor)

    def _buscar_cliente(self, cpf):
        for cliente in self.clientes:
            if cliente.cpf == cpf:
                return cliente
        raise ValueError("Cliente não encontrado.")
