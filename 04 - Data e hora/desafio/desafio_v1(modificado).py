import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
from typing import List
import re

class ContasIterador:
    def __init__(self: object, contas: list) -> None:
        if not isinstance(contas, list):
            raise TypeError("O parâmetro 'contas' deve ser uma lista.")
        self.contas = contas
        self._index = 0

    def __iter__(self: object) -> object: 
        return self

    def __next__(self: object) -> str:
        if self._index >= len(self.contas):
            raise StopIteration
        
        conta = self.contas[self._index]
        self._index += 1
        return (
            f"Agência: {conta.agencia}\n"
            f"Número: {conta.numero}\n"
            f"Titular: {conta.cliente.nome}\n"
            f"Saldo: R${conta.saldo:.2f}\n"
        )
    def reiniciar(self: object) -> None:
        #Reinicia o _index do contador de contas iteradas
        self._index = 0

class Cliente:
    def __init__(self: object, endereco: str) -> None:
        self.endereco: str = endereco
        self.contas: List[Conta] = []
        self.indice_conta = 0
        self.limite_transacoes_diarias: int = 10

    def realizar_transacao(self, conta: 'Conta', transacao: 'Transacao') -> None:
        # Validar o número de transações do dia
        transacoes_do_dia = conta.historico.transacoes_do_dia()
        if len(transacoes_do_dia) >= self.limite_transacoes_diarias:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return

        # Realizar a transação se o limite não foi excedido
        transacao.registrar(conta)
        print("\n=== Transação realizada com sucesso! ===")

    def adicionar_conta(self, conta: 'Conta') -> None:
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        if self.validar_cpf(cpf):
            self.cpf = cpf
        else:
            raise ValueError("CPF inválido.")

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        # Exemplo básico de validação de CPF (apenas formato)
        return bool(re.match(r"^\d{11}$", cpf))  # Valida se o CPF tem exatamente 11 dígitos

class Conta:
    def __init__(self, numero: int, cliente: PessoaFisica):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: PessoaFisica, numero: int) -> 'Conta':
        return cls(numero, cliente)

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def numero(self) -> int:
        return self._numero

    @property
    def agencia(self) -> str:
        return self._agencia

    @property
    def cliente(self) -> PessoaFisica:
        return self._cliente

    @property
    def historico(self) -> 'Historico':
        return self._historico

    def sacar(self, valor: float) -> bool:
        # Verifica se o valor informado é válido
        if not isinstance(valor, (int, float)) or valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        # Verifica se há saldo suficiente
        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        # Realiza o saque
        self._saldo -= valor
        self._historico.adicionar_transacao('Saque', valor)
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor: float) -> bool:
        # Verifica se o valor informado é válido
        if not isinstance(valor, (int, float)) or valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        # Realiza o depósito
        self._saldo += valor
        self._historico.adicionar_transacao('Depósito', valor)
        print("\n=== Depósito realizado com sucesso! ===")
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self) -> list:
        return self._transacoes

    def adicionar_transacao(self, tipo: str, valor: float) -> None:
        self._transacoes.append(
            {
                "tipo": tipo,
                "valor": valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self: object)-> (list):
        hoje = datetime.now().strftime("%d-%m-%Y")
        transacoes_hoje = [
            transacao for transacao in self._transacoes if transacao["data"].startswith(hoje) and transacao["data"].endswith(hoje)
        ]
        return transacoes_hoje
    def mostrar_historico(self) -> None:
        if not self._transacoes:
            print("\nNenhuma transação registrada.")
        else:
            print("\n=== Histórico de Transações ===")
            for transacao in self._transacoes:
                print(f"{transacao['data']}: {transacao['tipo']} de R$ {transacao['valor']:.2f}")


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()}")
        return resultado

    return envelope


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return
    
    print("\nContas disponíveis:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"[{i}] {conta.agencia} - {conta.numero} (Saldo: R$ {conta.saldo:.2f})")
        
    opcao = int(input("Escolha o número da conta: ")) - 1
    
    if 0<= opcao < len(cliente.contas):
        return cliente.contas[opcao]
    else:
        print("\n@@@ Opção inválida! @@@")
        return None


@log_transacao
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    extrato = ""
    tem_transacao = False
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['tipo']} - R$ {transacao['valor']:.2f} em {transacao['data']}"

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    # NOTE: O valor padrão de limite de saques foi alterado para 50 saques
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, limite_saques=50)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
