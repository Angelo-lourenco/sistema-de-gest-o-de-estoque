import sqlite3
import sqlite3 as sq

con = sq.connect('estoque.db')
cur = con.cursor()
con_1 = sq.connect('itens_de_cadastro.db')
cur_1 = con_1.cursor()


class Posicao:

    def __init__(self, codigo_posicao):
        self._codigo_posicao = codigo_posicao

    # FUNÇÕES DE MANIPULAÇÃO DE POSIÇÃO;
    @staticmethod
    def _cria_posicao_():
        codigo = input('Digite o código da posição a qual deseja cadastrar.\n Digite: ').strip().upper()
        posicao_criada = Posicao(codigo)
        cur.execute(f'''CREATE TABLE "{posicao_criada._codigo_posicao}" ("codigo" TEXT NOT NULL UNIQUE, 
                                                           "descricao" TEXT NOT NULL UNIQUE, 
                                                           "quantidade" INTEGER NOT NULL, 
                                                            PRIMARY KEY("codigo")); ''')

    @staticmethod
    def _exclui_posicao_(codigo):
        cur.execute(f'DROP TABLE IF EXISTS {codigo}')
        con.commit()

    # FUNÇÕES DE MANIPULAÇÃO DE ITENS;
    @staticmethod
    def _aloca_itens_():

        # Recebe as informações para alocagem dos itens (código do item e a quantidade a ser alocada);
        codigo_item, quantidade_de_alocagem = (
            input('Digite o código do item a ser alocado.\n Código: ').strip().upper(),
            input('Digite a quantidade de itens que deseja alocar na posicao.\n Quantiade: ').strip().upper())

        # Realiza a seleção do item no banco de dados que possui todos os itens de uso cadastrados;
        cur_1.execute(f'SELECT * FROM itens WHERE codigo = "{codigo_item}"')
        resultado_query = cur_1.fetchone()

        # Cria um objeto do tipo "Item" que servirá de base para a alocagem do item na posição;
        item_de_alocagem = Item(resultado_query[0], resultado_query[1])

        # Recebe o código da posição que o item será alocado;
        codigo_posicao = input('Digite a posição que deseja alocar o item.\n'
                               ' Posição:  ').strip().upper()

        # Cria um objeto "Posicao" que será responsável por representar a posição que alocará o item;
        posicao_de_alocagem = Posicao(codigo_posicao)

        # Verifica se a posição ja possui alguma quantidade deste item específico alocado nela;
        cur.execute(f'SELECT * FROM "{codigo_posicao}" WHERE codigo = "{item_de_alocagem.codigo_item}"; ')

        # Caso possua o item alocado;
        if cur.fetchone():

            # Realiza a soma das quantidades no banco de dados no registro do item específico;
            cur.execute(
                f'UPDATE "{posicao_de_alocagem._codigo_posicao}"'
                f'SET quantidade = quantidade + "{quantidade_de_alocagem}" '
                f'WHERE codigo = "{item_de_alocagem.codigo_item}"')

            con.commit()

        # caso não possua o item previamente alocado;
        else:

            # Insere o item na posição de alocagem selecionada;
            cur.execute(f'INSERT INTO "{posicao_de_alocagem._codigo_posicao}" '
                        f'(codigo, descricao, quantidade) VALUES '
                        f'("{item_de_alocagem.codigo_item}", '
                        f'"{item_de_alocagem.descricao}", '
                        f'"{quantidade_de_alocagem}"); ')
            con.commit()
            con.close()

    @staticmethod
    def _localiza_item_():

        # Recebo o valor do item ao qual desejo realizar a busca;
        codigo_do_item = input('Digite o código do item que deseja localizar.\n Digite: ')

        # Seleciono todas as tabelas existentes no meu banco de dados;
        cur.execute('SELECT name FROM sqlite_master WHERE type="table"; ')
        catalogo_posicoes = cur.fetchall()

        # Crio uma lista a qual armazenará todas as tabelas (ou posições) do meu banco de dados que possuem o item buscado;
        posicoes_com_o_item = []

        # Realizo um loop por todo o catálogo de posições;
        for posicao in catalogo_posicoes:
            nome_posicao = posicao[0]
            cur.execute(f'SELECT * FROM "{nome_posicao}" WHERE codigo = "{codigo_do_item}"; ')
            infos_dos_itens = cur.fetchall()
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


''' A classe "Item" somente opera suas funções no banco de dados "itens_de_cadastro". Sendo assim, qualquer atividade de 
manipulação de itens, seja transferência, retirada ou exclusão ou localização de itens de uma posição, deve ser realizada através
de funções da classe "Posicao" '''


class Item:

    def __init__(self, codigo_item, descricao):
        self._codigo_item = codigo_item
        self._descricao = descricao
        self.quantidade = 0

    def __str__(self):
        return(f'Código : {self._codigo_item}\n'
               f'Descrição : {self._descricao}')

    # funções do banco de dados "Itens";
    @staticmethod
    def _cadastra_item_():
        codigo, descricao = (input('Digite o código do item a ser cadastrado no sistema.\n Código: ').strip().upper(),
                             input(
                                 'Digite a descrição so item a ser cadastrado no sistema.\n Descrição: ').strip().upper())

        try:
            item_de_cadastro = Item(codigo, descricao)
            cur_1.execute(
                f'INSERT INTO itens VALUES ("{item_de_cadastro._codigo_item}", "{item_de_cadastro._descricao}"); ')
            con_1.commit()
            con_1.close()

        except sqlite3.IntegrityError:
            print('Código ou descrição já cadastrado no sistema!')
            Item._cadastra_item_()

    @staticmethod
    def _exclui_item_():
        try:
            codigo = input('Digite o código do item a ser excluído do sistema.\n Código: ').strip().upper()
            cur_1.execute(f'DELETE FROM itens WHERE codigo = "{codigo}"; ')
            con_1.commit()
            con_1.close()

            if cur_1.rowcount == 0:
                print('Nenhum item com esse código encontrado no sistema.')
                Item._exclui_item_()

            else:
                print('Item removido com sucesso.')

        except sqlite3.Error as e:
            print(f'Erro ao remover o registro {e}')
            Item._exclui_item_()


    @staticmethod
    def retorna_catalogo_de_itens():
        cur_1.execute('SELECT * FROM itens')
        catalogo = cur_1.fetchall()
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

