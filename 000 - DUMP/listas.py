def analise_vendas(vendas):
    # TODO: Calcule o total de vendas e realize a média mensal:
    total_vendas = sum(vendas)
    media_vendas = total_vendas / 12
    return f"{total_vendas}, {media_vendas:.2f}"

def obter_entrada_vendas():
    # Solicita a entrada do usuário em uma única linha
    entrada = input()
    vendas = entrada.split(',')
    
    # TODO: Converta a entrada em uma lista de inteiros:
    vendas = list(map(int, vendas))
    
    return vendas

vendas = obter_entrada_vendas()
print(analise_vendas(vendas))