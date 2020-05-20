import sys
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMainWindow, QFileDialog
from gui import mobilitat_programa
import pandas as pd
import numpy as np

class Mobilitat_Aplicacion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = mobilitat_programa()
        self.ui.setupUi(self)

        self.ui.btn_add_vacant.clicked.connect(self.add_vacant)
        self.ui.btn_assignacio_automatica.clicked.connect(self.programa)
        self.ui.mni_peticions.triggered.connect(self.carrega_peticions)
        self.ui.mni_vacants.triggered.connect(self.carrega_vacants)
        self.ui.mni_personal.triggered.connect(self.carrega_personal)
        self.ui.mni_sortir.triggered.connect(self.sortir)
        self.ui.btn_guarda_assig.clicked.connect(self.guarda_assignacions)
        self.ui.btn_assignacio_manual.clicked.connect(self.assignar_vacant_manual)
        self.ui.cbx_categoria_general.currentIndexChanged.connect(self.actualitza_pantalles)


    def carrega_peticions(self):
        try:
            path_peticions, _ = QFileDialog.getOpenFileName(self, 'Carrega peticions', r'C:\\Users\\Usuario\\Desktop\\Python Projects\\Mobilidad','CSV Files(*.csv)')
            peticions_nan = pd.read_csv(path_peticions, sep=";", encoding='latin1')
            self.peticiones = peticions_nan.replace(np.nan, '', regex=True)
            self.peticions = self.peticiones
            print("S'han carregat correctament les peticions")
            print(self.peticions.to_string())
        except Exception as e:
            print(e)
            print("No s'han carregat correctament les peticions, torni a provar")

    def carrega_personal(self):
        try:
            path_personal, _ = QFileDialog.getOpenFileName(self, 'Carrega personal',
                                                     r'C:\\Users\\Usuario\\Desktop\\Python Projects\\Mobilidad\\Programa',
                                                     'Excel Files(*.xlsx)')

            self.df_personal = pd.read_excel(path_personal, sep=",", encoding='latin1')

            # Cargamos personal
            #self.df_personal = pd.read_excel(r'C:\Users\Usuario\Desktop\Python Projects\Mobilidad\Programa\personal2.xlsx')

            # Obtenemos el numero de personas por parque-turno y categoria
            self.df_personal['TOTAL_GRUP'] = self.df_personal.groupby(['PARC_ORIGEN', 'CATEGORIA'])['CATEGORIA'].transform('count')

            self.df_personal = self.df_personal.drop(['MATRICULA'], axis=1)

            self.df_personal = self.df_personal.drop_duplicates()

            print('Has aqui guay')

            print(set(self.df_personal.index))


            # Pasamos a indice la columna parc_origen
            try:
                self.df_personal =self.df_personal.pivot(index='PARC_ORIGEN', columns='CATEGORIA', values='TOTAL_GRUP')
            except Exception as e:
                print(e)

            # Funciona para conseguir el valor deseado
            # cantidad = self.df_personal.loc[parc_torn,categoria].values[0]
            self.pintar_table_estat_parcs()

        except Exception as e:
            print(e)
            print("No s'han carregat correctament el personal, torni a provar")

    def carrega_vacants(self):
        try:
            path_vacants, _ = QFileDialog.getOpenFileName(self, 'Carrega vacants',
                                                     r'C:\\Users\\Usuario\\Desktop\\Python Projects\\Mobilidad',
                                                     'Excel Files(*.xls)')

            self.df_vacantes = pd.read_excel(path_vacants, index_col=0, sep=",", encoding='latin1')

            self.vacantes = self.df_vacantes

            self.df_moviments = pd.DataFrame()
            self.afegir_vacants = pd.DataFrame()
            self.categoria = ''

            print("S'han carregat correctament les vacants/excessos")
            print(self.df_vacantes.to_string())
        except Exception as e:
            print("No s'han carregat correctament les vacants/excessos, torni a provar")

        self.df_moviments = pd.DataFrame()
        self.afegir_vacants = pd.DataFrame()
        self.pintar_table_vacants()

    def add_vacant(self):
        print(self.vacantes)

        # Capturamos la seleccion en el menu Afegir Vacant
        aux = transforma_parc(self.ui.cbx_parc.itemText(self.ui.cbx_parc.currentIndex()))
        parc = [aux]
        torn = self.ui.cbx_torn.itemText(self.ui.cbx_torn.currentIndex())
        print("punto 1")
        categoria = self.ui.cbx_bomber.itemText(self.ui.cbx_bomber.currentIndex())
        print("punto 2")
        quantitat = int(self.ui.led_vacants.text())
        print(parc,torn,categoria,quantitat)
        #aux = []
        #aux.append(categoria)
        options = [categoria]


        # Llegim l'estat:
        estat_desti = int(self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn])
        print(estat_desti)

        # Modiquem l'estat:

        self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn] = estat_desti + quantitat
        estat_desti_post = self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn]
        print(estat_desti_post)
        print(self.vacantes.to_string())

        df = pd.DataFrame(
            {'parc': parc, 'torn': torn, 'categoria': categoria,
             'quantitat': quantitat}, index=[0])
        print("punto 4")
        # print(df)
        self.afegir_vacants = self.afegir_vacants.append(df, ignore_index=True)
        print("punto 5")
        self.pinta_vacants()
        print("punto 6")
        self.pintar_table_vacants()

    def assignar_vacant_manual(self):
        #print(self.vacantes)

        # Capturamos la seleccion en el menu Afegir Vacant
        aux = transforma_parc(self.ui.cbx_parc_assignacio.itemText(self.ui.cbx_parc.currentIndex()))
        parc = [aux]
        torn = self.ui.cbx_torn_assignacio.itemText(self.ui.cbx_torn.currentIndex())
        categoria = self.ui.cbx_categoria_general.itemText(self.ui.cbx_bomber.currentIndex())
        usuari = int(self.ui.led_matricula_assignacio.text())
        options = [categoria]
        desti_nou = ''
        try:
            desti_nou = self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_NOU'].values
            desti_nou = desti_nou[0]
            print(desti_nou)
        except Exception as e:
            print(e)
        if len(desti_nou) <= 0:
            try:
                origen = self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_ACTUAL'].values
                origen = origen[0]
            except Exception as e:
                print(e)
        else:
            origen = self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_NOU'].values
            print("Ja tenia destí assignat", origen)
            #aux = self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_NOU']
            #print(aux.values, aux.shape)
            #origen = aux.values
            # Pasamos
            origen = origen[0]

        try:
            parc_origen, torn_origen = self.info_split(origen)
            print(parc_origen, torn_origen)
            array_parc_origen = [parc_origen]
        except Exception as e:
            print(e)

        ## Modifiquem origen
        print("Anem a modificar origen")
        try:
            estat_origen = int(self.vacantes.loc[(self.vacantes.index.isin(array_parc_origen) & self.vacantes['CATEGORIA'].isin(options)), torn_origen])
            print(estat_origen)
            self.vacantes.loc[(self.vacantes.index.isin(array_parc_origen) & self.vacantes['CATEGORIA'].isin(options)), torn_origen] = estat_origen + 1
            estat_origen_post = int(self.vacantes.loc[(self.vacantes.index.isin(array_parc_origen) & self.vacantes['CATEGORIA'].isin(options)), torn_origen])
            print(estat_origen_post)
        except Exception as e:
            print(e)

        # Modifiquem desti
        try:

            print("Anem a modificar desti")
            estat_desti = int(self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn])
            print(estat_desti)
            self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn] = estat_desti - 1
            estat_desti_post = int(self.vacantes.loc[(self.vacantes.index.isin(parc) & self.vacantes['CATEGORIA'].isin(options)), torn])
            print(estat_desti_post)
        except Exception as e:
            print(e)

        # Modificar destino usuario en peticiones (comprobar si ya se le habia asignado un destino)
        try:
            pet = str(parc[0]) + str('-') + str(torn[0])
            print(pet)
        except Exception as e:
            print(e)
        try:
            print(desti_nou[0])
            self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_NOU'] = pet
        except Exception as e:
            print(e)

        # Crear movimiento

        df = pd.DataFrame(
            {'Matricula': usuari, 'origen': origen,
             'estat_origen_post': estat_origen_post, 'desti': pet,
             'estat_desti_post': estat_desti_post}, index=[0])

        # Añadimos el movimiento a df_movimientos
        self.df_moviments = self.df_moviments.append(df, ignore_index=True)

        self.actualitza_pantalles()

    def info_split(self, info):
        parc = info.split('-')[0]
        torn = info.split('-')[1]
        return parc, torn

    def pinta_vacants(self):
        vacants_afegides = self.afegir_vacants.values.tolist()

        #   resultados = dataframe datos
        self.ui.table_vacants.clearContents()
        row = 0
        for vacante in vacants_afegides:
            self.ui.table_vacants.setRowCount(row + 1)
            print(vacante)

            matricula = QTableWidgetItem(str(vacante[0]))

            self.ui.table_vacants.setItem(row, 0, matricula)
            self.ui.table_vacants.setItem(row, 1, QTableWidgetItem(str(vacante[1])))
            self.ui.table_vacants.setItem(row, 2, QTableWidgetItem(str(vacante[2])))
            self.ui.table_vacants.setItem(row, 3, QTableWidgetItem(str(vacante[3])))
            #self.ui.table_vacants.setItem(row, 4, QTableWidgetItem(str(vacante[4])))

            row += 1

    def usuari_buscar_desti(self, row):

        # Inicialitzem la posible resulta:
        df_tirada = pd.DataFrame()
        repetir = 0

        # Adquirim les peticions de l'usuari:
        desti_nou_assignat = row[1][2]
        usuari = row[1][0]
        peticions_usuari = []
        for opcions in np.arange(7, 15, 1):
            if row[1][opcions] != '':
                peticions_usuari.append(str(row[1][opcions]))

        #print("Peticions d'usuari {} {}".format(usuari, peticions_usuari))

        print("el desti nou {} i la seva longitud {}".format(desti_nou_assignat, len(desti_nou_assignat)))
        #desti_nou_assignat = [desti_nou_assignat]
        if len(desti_nou_assignat) > 0:
            try:
                posicio = peticions_usuari.index(desti_nou_assignat)
            except Exception as e:
                print(e)
            peticions_usuari = peticions_usuari[:posicio]
            origen = desti_nou_assignat
            print("origen assignat: ",origen)
        else:
            origen = str(row[1][1])
            print("origen assignat: ", origen)


        print("origen assignat: ",origen)
        print("Peticions d'usuari {} {}".format(usuari, peticions_usuari, desti_nou_assignat))

        # input('Pulsa para realizar la busqueda con estas peticiones')

        nou_desti = 0
        #print(nou_desti)
        #print("Entramos en el bucle peticions")

        #### HEMOS CAMBIADO ESTO ANTES ERA = ['BOMBERS'] AHORA ESTE SE ACTUALIZA CON EL CAMBIO DEL COMBOBOX
        options = ['BOMBER']
        for pet in peticions_usuari:
            print(origen)
            print("Entramos en el bucle peticions con", pet)
            # Amb desti_nou el que fem es que evitar recorrer totes les peticions,una vegada tenim una ja parem
            if nou_desti == 0:
                usuari = row[1][0]
                print("L'usuari {} demana la peticio {}:".format(usuari, pet))
                parc_desti, torn_desti = self.info_split(pet)
                print(parc_desti,torn_desti)
                parc_desti_array = [parc_desti]
                print(parc_desti_array)


                estat_desti = int(self.vacantes.loc[(self.vacantes.index.isin(parc_desti_array) & self.vacantes['CATEGORIA'].isin(options)), torn_desti])
                print(estat_desti)


                parc_origen, torn_origen = self.info_split(origen)

                print(parc_origen,torn_origen)
                parc_origen_array = [parc_origen]
                print(parc_origen_array)

                estat_origen = int(self.vacantes.loc[(self.vacantes.index.isin(parc_origen_array) & self.vacantes['CATEGORIA'].isin(options)), torn_origen])
                print("estat origen: ",estat_origen)
                #estat_origen = int(self.vacantes[torn_origen][parc_origen])

                #print("origen: ",parc_origen,torn_origen)

                # Controlem els que tenen com a primera opció l'origen:

                if pet == origen:
                    # Si son iguales y en destino/origen hay exceso, no puede quedar
                    # Comprovem l'estat a origen
                    estat_origen = int(self.vacantes.loc[(self.vacantes.index.isin(parc_origen_array) & self.vacantes['CATEGORIA'].isin(options)), torn_origen])
                    print(estat_origen)
                    #estat_origen = int(self.vacantes[torn_origen][parc_origen])
                    print("Llego hasta aqui 1")
                    if estat_origen < 0:
                        print("Hi ha exces i per tant ha de marxar")
                    else:
                        print("No hi ha exces, no cal que marxi")
                        self.vacantes.loc[(self.vacantes.index.isin(parc_desti_array) & self.vacantes['CATEGORIA'].isin(options)), torn_desti] = estat_desti + 1
                        #self.vacantes[torn_desti][parc_desti] = estat_desti + 1

                #print("Hem comprovat si l'origen era igual a la peticio")
                # Busquem
                print(origen)
                print("Llego hasta aqui 2")
                print(estat_desti)
                if estat_desti <= 0: # No hi ha vacants, esta equilibrat o hi ha exces.
                    print("Aquest parc no esta disponible ara mateix")
                else: # No hi ha exces
                    # print("En el desti {}-{} hi ha {} vacants".format(parc_desti, torn_desti, estat_desti))
                    # print(df_vacantes)
                    print("Llego hasta aqui 2.1")
                    self.peticions.loc[self.peticions['MATRICULA'] == usuari, 'DESTI_NOU'] = pet

                    ### AQUI JA HEM ASSIGNAT LA VACANT

                    # Restem a personal 1 unitat al parc origen i sumem al parc destí

                    #parc_origen_array
                    #cantidad = self.df_personal.loc[parc_torn, categoria].values[0]
                    print("IMPRIMO PARCS",origen, parc_origen_array)
                    personal_origen = self.df_personal.loc[origen,options].values[0]
                    print("peticio",pet)
                    pet_array = [pet]
                    personal_desti = self.df_personal.loc[pet_array, options].values[0]
                    print("personal desti:", personal_desti)

                    print("personal origen:", personal_origen)
                    #print ("persona destion: ", personal_desti)
                    self.df_personal.loc[origen,options] = personal_origen - 1
                    self.df_personal.loc[pet_array, options] = personal_desti + 1


                    # combrim una vacant a desti i per tant, restem una vacant disponible
                    print("Llego hasta aqui 2.2")
                    self.vacantes.loc[(self.vacantes.index.isin(parc_desti_array) & self.vacantes['CATEGORIA'].isin(options)),torn_desti] = estat_desti - 1
                    #self.vacantes[torn_desti][parc_desti] = estat_desti - 1

                    estat_desti_post = int(self.vacantes.loc[(self.vacantes.index.isin(parc_desti_array) & self.vacantes['CATEGORIA'].isin(options)), torn_desti])
                    print("Llego hasta aqui 2.3")
                    # print("estado :{}".format(estat_desti_post))
                    if estat_desti_post <= 0:
                        print("Ja no queden mes vacants en el destí asignat")
                    else:
                        print("Encara hi ha {} vacants en el desti {}-{}".format(estat_desti_post, parc_desti,torn_desti))
                    print("Llego hasta aqui 2.4")

                    # Sumem la vacant que acabem de generan en origen o exces que hem cobert
                    self.vacantes.loc[(self.vacantes.index.isin(parc_origen_array) & self.vacantes['CATEGORIA'].isin(options)), torn_origen] = estat_origen + 1
                    #self.vacantes[torn_origen][parc_origen] = estat_origen + 1
                    print("Llego hasta aqui 2.5")
                    estat_origen_post = int(self.vacantes.loc[(self.vacantes.index.isin(parc_origen_array) & self.vacantes['CATEGORIA'].isin(options)), torn_origen])

                    print("Llego hasta aqui 3")
                    if estat_origen_post <= 0:
                        print("No s'allibera vacant, ha cobrit un exces")
                    else:
                        print("Hi ha {} vacants a {}-{}".format(estat_origen_post, parc_origen,torn_origen))

                        # Activem repetir quan volem tornar al principi de la llista. Es el valor a retornar.
                        repetir = 1
                    # Guardem el moviment realitzat:
                    df = pd.DataFrame(
                        {'Matricula': usuari, 'origen': origen,
                         'estat_origen_post': estat_origen_post, 'desti': pet,
                         'estat_desti_post': estat_desti_post}, index=[0])

                    #print(df)
                    df_tirada = df_tirada.append(df, ignore_index=True)

                    print("Vacant assignada!")

                    # input('Analiza lo sucedido')
                    nou_desti = 1
        return df_tirada, repetir, usuari

    def pintar_table_estat_parcs(self):
        # table_estat_parcs


        datos = self.df_personal.values.tolist()


        #   resultados = dataframe datos
        self.ui.table_estat_parcs.clearContents()
        row = 0
        for parc_estats in datos:


            self.ui.table_estat_parcs.setRowCount(row + 1)

            self.ui.table_estat_parcs.setItem(row, 0, QTableWidgetItem(str(parc_estats[2])))
            self.ui.table_estat_parcs.setItem(row, 1, QTableWidgetItem(str(parc_estats[1])))
            self.ui.table_estat_parcs.setItem(row, 3, QTableWidgetItem(str(parc_estats[0])))
            #self.ui.table_estat_parcs.setItem(row, 3, QTableWidgetItem(str(parc_estats[3])))
            #self.ui.table_estat_parcs.setItem(row, 4, QTableWidgetItem(str(parc_estats[4])))

            row += 1
        labels = self.df_personal.index
        print(labels)
        self.ui.table_estat_parcs.setVerticalHeaderLabels(labels)

    def pintar_table_vacants(self):

        print(self.categoria)
        print("comencem a pintar vacants")
        estats_categoria = self.vacantes['CATEGORIA'] == self.categoria
        print(" he aconseguit l'estat de la categoria")
        print(self.vacantes[estats_categoria])

        datos = self.vacantes[estats_categoria].values.tolist()


        #   resultados = dataframe datos
        self.ui.table_vacants_estat.clearContents()
        row = 0
        for parc_estats in datos:
            self.ui.table_vacants_estat.setRowCount(row + 1)

            self.ui.table_vacants_estat.setItem(row, 0, QTableWidgetItem(str(parc_estats[0])))
            self.ui.table_vacants_estat.setItem(row, 1, QTableWidgetItem(str(parc_estats[1])))
            self.ui.table_vacants_estat.setItem(row, 2, QTableWidgetItem(str(parc_estats[2])))
            self.ui.table_vacants_estat.setItem(row, 3, QTableWidgetItem(str(parc_estats[3])))
            self.ui.table_vacants_estat.setItem(row, 4, QTableWidgetItem(str(parc_estats[4])))


            row += 1

        labels_vacants = ['EX', 'LL', 'MJ', 'SA', 'VH']
        self.ui.table_vacants_estat.setVerticalHeaderLabels(labels_vacants)
    def pintar_table_movimientos(self):

        datos = self.df_moviments.values.tolist()

        #   resultados = dataframe datos
        self.ui.table_movimientos.clearContents()
        row = 0
        for vacante in datos:
            self.ui.table_movimientos.setRowCount(row + 1)

            matricula = QTableWidgetItem(str(vacante[0]))

            self.ui.table_movimientos.setItem(row, 0, matricula)
            self.ui.table_movimientos.setItem(row, 1, QTableWidgetItem(str(vacante[1])))
            self.ui.table_movimientos.setItem(row, 2, QTableWidgetItem(str(vacante[2])))
            self.ui.table_movimientos.setItem(row, 3, QTableWidgetItem(str(vacante[3])))
            self.ui.table_movimientos.setItem(row, 4, QTableWidgetItem(str(vacante[4])))

            row += 1

    def actualitza_pantalles(self):
        self.categoria = self.ui.cbx_categoria_general.itemText(self.ui.cbx_bomber.currentIndex())
        self.pintar_table_vacants()
        self.pinta_vacants()
        self.pintar_table_movimientos()
        self.pintar_table_estat_parcs()

    def programa(self):
        for row in self.peticions.iterrows():
            print(row)
            df, repetir, usuari = self.usuari_buscar_desti(row)
            self.df_moviments = self.df_moviments.append(df, ignore_index=True)
            if repetir == 1:
                break

        print("Modificamos la vista moviments:\n", self.df_moviments)
        print("Asi estan las peticions\n", self.peticions)
        self.actualitza_pantalles()
        #self.pintar_table_movimientos(df_moviments)



    def guarda_assignacions(self):
        # Exportamos los datos

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('resultats.xlsx', engine='xlsxwriter')

        # Convert the dataframe to an XlsxWriter Excel object.
        self.peticions.to_excel(writer, sheet_name='Peticions_resoltes')
        self.vacantes.to_excel(writer, sheet_name='Vacants_finals')
        self.df_moviments.to_excel(writer, sheet_name='Moviments_realitzats')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    def sortir(self):
        # Exportamos los datos
        pd.self.peticions.to_excel('peticions_asignades.xls')
        pd.self.vacantes.to_excel('estat_vacants.xls')
        pd.self.df_moviments.to_excel('Mobilitat_moviments.xls')

        # Salimos del programa
        sys.exit(0)


def transforma_parc(parc):
    parc_dict = {'EX': 'EIXAMPLE', 'LL':'LLEVANT', 'MJ':'MONTJUIC','SA':'SANT ANDREU','VH':'VALL HEBRON'}
    for sigla_parc, parc_ in parc_dict.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if parc_ == parc:
            return sigla_parc


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = Mobilitat_Aplicacion()
    ventana.show()


    sys.exit(app.exec_())