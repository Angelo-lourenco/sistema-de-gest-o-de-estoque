import sqlite3 as sq

conn_estoque = sq.connect('estoque.db')
cur_estoque = conn_estoque.cursor()
conn_catalogo = sq.connect('itens_de_cadastro.db')
cur_catalogo = conn_catalogo.cursor()


class Posicao:

    def __init__(self, codigo_posicao):
        self._codigo_posicao = codigo_posicao
        self._itens = []

    # FUNÇÕES DE MANIPULAÇÃO DE POSIÇÃO;
    @staticmethod
    def _cria_posicao_():
        codigo = input('Digite o código da posição a qual deseja cadastrar.\n Digite: ').strip().upper()
        posicao_criada = Posicao(codigo)
        cur_estoque.execute(f'''CREATE TABLE "{posicao_criada._codigo_posicao}" ("codigo" TEXT NOT NULL UNIQUE, 
                                                           "descricao" TEXT NOT NULL UNIQUE, 
                                                           "quantidade" INTEGER NOT NULL, 
                                                            PRIMARY KEY("codigo")); ''')
        conn_estoque.commit()

    @staticmethod
    def _exclui_posicao_(codigo):
        cur_estoque.execute(f'DROP TABLE IF EXISTS {codigo}')
        conn_estoque.commit()

    # FUNÇÕES DE MANIPULAÇÃO DE ITENS;
    @staticmethod
    def _aloca_item_():

        # Recebe as informações para alocagem dos itens (código do item e a quantidade a ser alocada);
        codigo_item, quantidade_de_alocagem = (
            input('Digite o código do item a ser alocado.\n Código: ').strip().upper(),
            input('Digite a quantidade de itens que deseja alocar na posicao.\n Quantiade: ').strip().upper())

        # Realiza a seleção do item no banco de dados que possui todos os itens de uso cadastrados;
        cur_catalogo.execute(f'SELECT * FROM itens WHERE codigo = "{codigo_item}"')
        resultado_query = cur_catalogo.fetchone()

        # Cria um objeto do tipo "Item" que servirá de base para a alocagem do item na posição;
        item_de_alocagem = Item(resultado_query[0], resultado_query[1])

        # Recebe o código da posição que o item será alocado;
        codigo_posicao = input('Digite a posição que deseja alocar o item.\n'
                               ' Posição:  ').strip().upper()

        # Cria um objeto "Posicao" que será responsável por representar a posição que alocará o item;
        posicao_de_alocagem = Posicao(codigo_posicao)

        # Verifica se a posição ja possui alguma quantidade deste item específico alocado nela;
        cur_estoque.execute(f'SELECT * FROM "{codigo_posicao}" WHERE codigo = "{item_de_alocagem.codigo_item}"; ')

        # Caso possua o item alocado;
        if cur_estoque.fetchone():

            # Realiza a soma das quantidades no banco de dados no registro do item específico;
            cur_estoque.execute(
                f'UPDATE "{posicao_de_alocagem._codigo_posicao}"'
                f'SET quantidade = quantidade + "{quantidade_de_alocagem}" '
                f'WHERE codigo = "{item_de_alocagem.codigo_item}"')

            conn_estoque.commit()

        # caso não possua o item previamente alocado;
        else:

            # Insere o item na posição de alocagem selecionada;
            cur_estoque.execute(f'INSERT INTO "{posicao_de_alocagem._codigo_posicao}" '
                                f'(codigo, descricao, quantidade) VALUES '
                                f'("{item_de_alocagem.codigo_item}", '
                                f'"{item_de_alocagem.descricao}", '
                                f'"{quantidade_de_alocagem}"); ')
            conn_estoque.commit()
            conn_estoque.close()

    @staticmethod
    def _localiza_item_():

        global codigo_do_item

        # Recebo o valor do item ao qual desejo realizar a busca;
        codigo_do_item = input('Digite o código do item que deseja localizar.\n Digite: ')

        # Seleciono todas as tabelas existentes no meu banco de dados;
        cur_estoque.execute('SELECT name FROM sqlite_master WHERE type="table"; ')
        catalogo_posicoes = cur_estoque.fetchall()

        # Crio uma lista a qual armazenará todas as tabelas (ou posições) do meu banco de dados que possuem o item buscado;
        posicoes_com_o_item = []

        # Realizo um loop por todo o catálogo de posições;
        for posicao in catalogo_posicoes:
            nome_posicao = posicao[0]
            cur_estoque.execute(f'SELECT * FROM "{nome_posicao}" WHERE codigo = "{codigo_do_item}"; ')
            infos_dos_itens = cur_estoque.fetchall()
            if infos_dos_itens:
                posicoes_com_o_item.append((nome_posicao, infos_dos_itens))

        # Crio uma lista para armazenar todas as informações dos itens
        itens_da_posicao = []

        for nome_posicao, infos_dos_itens in posicoes_com_o_item:
            for info_do_item in infos_dos_itens:
                # Crie um novo dicionário para cada item
                atributos_do_item = {'Código': info_do_item[0],
                                     'Descrição': info_do_item[1],
                                     'Quantidade': info_do_item[2]}
                itens_da_posicao.append((nome_posicao, atributos_do_item))

        # Exiba as informações no final
        for nome_posicao, atributos_do_item in itens_da_posicao:
            print(f'Localizado na posição {nome_posicao}: ')
            print(f"Código: {atributos_do_item['Código']}\n"
                  f"Descrição: {atributos_do_item['Descrição']}\n"
                  f"Quantidade: {atributos_do_item['Quantidade']}\n"
                  f"-------------------------------------------------")

    @staticmethod
    def _retira_item():

        # Chamo a função "localiza_item()" para verificar quais posições possui o item buscado;
        Posicao._localiza_item_()

        # Recebo o imput do usuário de qual posição deseja fazer a retirada do item (com base nos resultados da função
        # "localiza_item()") e quantidades a serem retiradas;
        codigo_posicao_retirada = input('Digite a posição que deseja retirar o item:\n'
                                        ' Posição: ')
        quantidade_de_retirada = int(input('Digite a quantidade de itens que deseja retirar da posição:\n'
                                           ' Digite: '))

        # Faço a verificação das informações do registro do item que desejo realizar a retirada;
        cur_estoque.execute(f'SELECT * FROM "{codigo_posicao_retirada}" WHERE codigo = "{codigo_do_item}"; ')
        resultado = cur_estoque.fetchone()

        # Realizo uma validação para apenas realizar a retirada de itens, caso a quantidade a ser retirada seja menor ou
        # igual a quantidade de itens que possui alocado a posição;
        if quantidade_de_retirada <= resultado[2]:

            cur_estoque.execute(
                f'UPDATE "{codigo_posicao_retirada}" SET quantidade = quantidade - "{quantidade_de_retirada}" WHERE codigo = "{codigo_do_item}";')
            conn_estoque.commit()
            conn_estoque.close()

        # Caso a quantidade desejada para retirar seja maior que a quantidade alocada na posição;
        else:
            print('-----------------------------------------------------------------------------\n'
                  'ERRO! Você está tentando retirar mais itens do que a posição possui alocado.\n'
                  '-----------------------------------------------------------------------------')
            Posicao._retira_item()

''' A classe "Item" somente opera suas funções no banco de dados "itens_de_cadastro". Sendo assim, qualquer atividade de 
manipulação de itens, seja transferência, retirada ou exclusão ou localização de itens de uma posição, deve ser realizada através
de funções da classe "Posicao" '''


class Item:

    def __init__(self, codigo_item, descricao):
        self._codigo_item = codigo_item
        self._descricao = descricao
        self.quantidade = 0

    def __str__(self):
        return (f'Código : {self._codigo_item}\n'
                f'Descrição : {self._descricao}')

    # funções do banco de dados "Itens";
    @staticmethod
    def _cadastra_item_():
        codigo, descricao = (input('Digite o código do item a ser cadastrado no sistema.\n Código: ').strip().upper(),
                             input(
                                 'Digite a descrição so item a ser cadastrado no sistema.\n Descrição: ').strip().upper())

        try:
            item_de_cadastro = Item(codigo, descricao)
            cur_catalogo.execute(
                f'INSERT INTO itens VALUES ("{item_de_cadastro._codigo_item}", "{item_de_cadastro._descricao}"); ')
            conn_catalogo.commit()
            conn_catalogo.close()

        except sq.IntegrityError:
            print('Código ou descrição já cadastrado no sistema!')
            Item._cadastra_item_()

    @staticmethod
    def _exclui_item_():
        try:
            codigo = input('Digite o código do item a ser excluído do sistema.\n Código: ').strip().upper()
            cur_catalogo.execute(f'DELETE FROM itens WHERE codigo = "{codigo}"; ')
            conn_catalogo.commit()
            conn_catalogo.close()

            if cur_catalogo.rowcount == 0:
                print('Nenhum item com esse código encontrado no sistema.')
                Item._exclui_item_()

            else:
                print('Item removido com sucesso.')

        except sq.Error as e:
            print(f'Erro ao remover o registro {e}')
            Item._exclui_item_()

    @staticmethod
    def retorna_catalogo_de_itens():
        cur_catalogo.execute('SELECT * FROM itens')
        catalogo = cur_catalogo.fetchall()
        for item in catalogo:
            item_atual = Item(item[0], item[1])
            print(f'{item_atual}\n'
                  f'--------------------------------------')

    # Setters;
    @property
    def codigo_item(self):
        return self._codigo_item

    @property
    def descricao(self):
        return self._descricao


