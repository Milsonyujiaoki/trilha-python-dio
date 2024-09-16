import textwrap
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Union, Generator
import re


class ContasIterador:
    """
    Implementa um iterador para percorrer as contas de forma sequencial.
    """

    def __init__(self: object, contas: List['Conta']) -> None:
        if not isinstance(contas, list):
            raise TypeError("O parâmetro 'contas' deve ser uma lista.")
        self.contas = contas
        self._index = 0

    def __iter__(self: object) -> 'ContasIterador':
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
        """Reinicia o índice do iterador para começar do início."""
        self._index = 0


class Cliente:
    """
    Representa um cliente do banco com endereço e contas associadas.
    """

    def __init__(self: object, endereco: str) -> None:
        self.endereco: str = endereco
        self.contas: List['Conta'] = []
        self.limite_transacoes_diarias: int = 10
        self.limite_transferencias_diarias: int = 5

    def realizar_transacao(self, conta: 'Conta', transacao: 'Transacao') -> None:
        """
        Realiza uma transação em uma conta associada ao cliente,
        verificando os limites diários de transações e transferências.
        """
        # Validar o número de transações do dia
        transacoes_do_dia = conta.historico.transacoes_do_dia()
        if len(transacoes_do_dia) >= self.limite_transacoes_diarias:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return

        # Verificar limite de transferências
        transferencias_do_dia = [t for t in transacoes_do_dia if t["tipo"] == "Transferência"]
        if len(transferencias_do_dia) >= self.limite_transferencias_diarias:
            print("\n@@@ Você excedeu o número de transferências permitidas para hoje! @@@")
            return

        transacao.registrar(conta)
        print("\n=== Transação realizada com sucesso! ===")

    def adicionar_conta(self, conta: 'Conta') -> None:
        """Adiciona uma conta ao cliente."""
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """
    Subclasse de Cliente que representa uma pessoa física.
    Adiciona CPF, nome e data de nascimento com validação de CPF.
    """

    def __init__(self: object, nome: str, data_nascimento: str, cpf: str, endereco: str) -> None:
        super().__init__(endereco)
        self.nome: str = nome
        self.data_nascimento: str = data_nascimento
        if self.validar_cpf(cpf):
            self.cpf: str = cpf
        else:
            raise ValueError("CPF inválido.")

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida se o CPF tem exatamente 11 dígitos."""
        return bool(re.match(r"^\d{11}$", cpf))


class Conta:
    """
    Representa uma conta bancária genérica.
    """

    def __init__(self: object, numero: int, cliente: PessoaFisica) -> None:
        self._saldo: float = 0
        self._numero: int = numero
        self._agencia: str = "0001"
        self._cliente: PessoaFisica = cliente
        self._historico: Historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: PessoaFisica, numero: int) -> 'Conta':
        """Cria uma nova conta para o cliente."""
        return cls(numero, cliente)

    @property
    def saldo(self: object) -> float:
        return self._saldo

    @property
    def numero(self: object) -> int:
        return self._numero

    @property
    def agencia(self: object) -> str:
        return self._agencia

    @property
    def cliente(self: object) -> PessoaFisica:
        return self._cliente

    @property
    def historico(self: object) -> 'Historico':
        return self._historico

    def sacar(self: object, valor: float) -> bool:
        """
        Realiza um saque na conta, se houver saldo suficiente.
        """
        if not isinstance(valor, (int, float)) or valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        return True

    def depositar(self: object, valor: float) -> bool:
        """
        Realiza um depósito na conta, aumentando o saldo.
        """
        if not isinstance(valor, (int, float)) or valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        return True


class ContaCorrente(Conta):
    """
    Subclasse de Conta que representa uma conta corrente.
    Adiciona limite de saques e valor máximo para saques.
    """

    def __init__(self: object, numero: int, cliente: PessoaFisica, limite: float = 500, limite_saques: int = 3) -> None:
        super().__init__(numero, cliente)
        self._limite: float = limite
        self._limite_saques: int = limite_saques

    @classmethod
    def nova_conta(cls, cliente: PessoaFisica, numero: int, limite: float, limite_saques: int) -> 'ContaCorrente':
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self: object, valor: float) -> bool:
        """
        Realiza um saque, verificando se o limite de saques ou valor foi excedido.
        """
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"]
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

    def __str__(self: object) -> str:
        return (
            f"Agência: {self.agencia}\n"
            f"C/C: {self.numero}\n"
            f"Titular: {self.cliente.nome}\n"
        )


class Historico:
    """
    Armazena e gerencia as transações realizadas em uma conta.
    """

    def __init__(self: object) -> None:
        self._transacoes: List[dict] = []

    @property
    def transacoes(self: object) -> List[dict]:
        return self._transacoes

    def adicionar_transacao(self: object, tipo: str, valor: float) -> None:
        """Adiciona uma transação ao histórico, garantindo que não seja duplicada."""
        if self._transacoes and self._transacoes[-1]["tipo"] == tipo and self._transacoes[-1]["valor"] == valor:
            print("Transação duplicada detectada, não adicionada.")
            return
        self._transacoes.append(
            {
                "tipo": tipo,
                "valor": valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self: object, tipo_transacao: Union[str, None] = None) -> Generator[dict, None, None]:
        """
        Gera um relatório de todas as transações ou filtra por tipo.
        """
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self: object) -> List[dict]:
        """
        Retorna as transações realizadas no dia atual.
        """
        hoje = datetime.now().strftime("%d-%m-%Y")
        return [transacao for transacao in self._transacoes if transacao["data"].startswith(hoje)]

    def mostrar_historico(self: object) -> None:
        """
        Exibe o histórico de transações da conta.
        """
        if not self._transacoes:
            print("\nNenhuma transação registrada.")
        else:
            print("\n=== Histórico de Transações ===")
            for transacao in self._transacoes:
                print(f"{transacao['data']}: {transacao['tipo']} de R$ {transacao['valor']:.2f}")


class Transacao(ABC):
    """
    Classe abstrata para definir uma transação.
    """

    @property
    @abstractmethod
    def valor(self: object) -> float:
        pass

    @abstractmethod
    def registrar(self: object, conta: Conta) -> None:
        pass


class Saque(Transacao):
    """
    Classe que representa a operação de saque.
    """

    def __init__(self: object, valor: float) -> None:
        self._valor: float = valor

    @property
    def valor(self: object) -> float:
        return self._valor

    def registrar(self: object, conta: Conta) -> None:
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao("Saque", self.valor)


class Deposito(Transacao):
    """
    Classe que representa a operação de depósito.
    """

    def __init__(self: object, valor: float) -> None:
        self._valor: float = valor

    @property
    def valor(self: object) -> float:
        return self._valor

    def registrar(self: object, conta: Conta) -> None:
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao("Depósito", self.valor)


def log_transacao(func):
    """
    Decorator para registrar e logar transações realizadas no sistema.
    """

    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()} executado com sucesso.")
        return resultado

    return envelope


def menu() -> str:
    """
    Exibe o menu principal do sistema e solicita a opção do usuário.
    """
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNovo Cliente
    [lc]\tListar Clientes
    [ncc]\tNova Conta
    [lcc]\tListar Contas
    [t]\tTransferir
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf: str, clientes: List[PessoaFisica]) -> Union[PessoaFisica, None]:
    """
    Retorna o cliente com o CPF correspondente.
    """
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente: PessoaFisica) -> Union[Conta, None]:
    """
    Permite que o cliente selecione uma conta associada a ele.
    """
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    print("\nContas disponíveis:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"[{i}] {conta.agencia} - {conta.numero} (Saldo: R$ {conta.saldo:.2f})")

    opcao = int(input("Escolha o número da conta: ")) - 1
    return cliente.contas[opcao] if 0 <= opcao < len(cliente.contas) else None


@log_transacao
def depositar(clientes: List[PessoaFisica]) -> None:
    """
    Realiza a operação de depósito em uma conta de um cliente.
    """
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
def sacar(clientes: List[PessoaFisica]) -> None:
    """
    Realiza a operação de saque em uma conta de um cliente.
    """
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
def exibir_extrato(clientes: List[PessoaFisica]) -> None:
    """
    Exibe o extrato de uma conta de um cliente.
    """
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
def novo_cliente(clientes: List[PessoaFisica]) -> None:
    """
    Cria um novo cliente com os dados fornecidos.
    """
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


def listar_clientes(clientes: List[PessoaFisica]) -> None:
    """
    Exibe a lista de clientes cadastrados.
    """
    if not clientes:
        print("\nNenhum cliente cadastrado.")
        return

    print("\n=== Lista de Clientes ===")
    for cliente in clientes:
        print(f"Nome: {cliente.nome}, CPF: {cliente.cpf}, Endereço: {cliente.endereco}")
    print("\n=== Total de clientes: {} ===".format(len(clientes)))


@log_transacao
def criar_conta(numero_conta: int, clientes: List[PessoaFisica], contas: List[ContaCorrente]) -> None:
    """
    Cria uma nova conta corrente para um cliente existente.
    """
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, limite_saques=50)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas: List[ContaCorrente]) -> None:
    """
    Exibe a lista de contas cadastradas.
    """
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return

    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(conta))
    print("\n=== Total de contas: {} ===".format(len(contas)))


@log_transacao
def transferir(clientes: List[PessoaFisica]) -> None:
    """
    Realiza uma transferência entre contas de clientes diferentes.
    """
    cpf_origem = input("Informe o CPF do cliente remetente: ")
    cliente_origem = filtrar_cliente(cpf_origem, clientes)

    if not cliente_origem:
        print("\n@@@ Cliente remetente não encontrado! @@@")
        return

    conta_origem = recuperar_conta_cliente(cliente_origem)
    if not conta_origem:
        return

    cpf_destino = input("Informe o CPF do cliente destinatário: ")
    cliente_destino = filtrar_cliente(cpf_destino, clientes)

    if not cliente_destino:
        print("\n@@@ Cliente destinatário não encontrado! @@@")
        return

    conta_destino = recuperar_conta_cliente(cliente_destino)
    if not conta_destino:
        return

    valor = float(input("Informe o valor a ser transferido: "))

    if conta_origem.sacar(valor):
        conta_destino.depositar(valor)
        print("\n=== Transferência realizada com sucesso! ===")
    else:
        print("\n@@@ Falha na transferência! @@@")


def main() -> None:
    """
    Função principal que controla o fluxo do sistema bancário.
    """
    clientes: List[PessoaFisica] = []
    contas: List[ContaCorrente] = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nc":
            novo_cliente(clientes)

        elif opcao == "lc":
            listar_clientes(clientes)

        elif opcao == "ncc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lcc":
            listar_contas(contas)

        elif opcao == "t":
            transferir(clientes)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()
