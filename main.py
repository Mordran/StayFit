from flask import *
import sqlite3, hashlib

reset_db=False

app = Flask(__name__)
app.secret_key = b'vino432u90tu34093whttiuwqhut'


@app.route("/")
@app.route("/index.html")
def main():
    user,data=get_session()
    
    return render_template("inicio.html",username=user)

@app.route("/ingreso/",methods=["GET"])
def ingreso():
    return render_template("ingreso.html")
@app.route("/ingreso/",methods=["POST"])
def ingresoP():
    dbcon = sqlite3.connect("stayfit.db")
    dbex = dbcon.cursor()
    
    email,passw=request.form['email'],request.form['pass']
    hsh=H(request.form['pass'])
    
    dbex.execute("SELECT * FROM usuarios WHERE (correo=?)",[email])
    res=dbex.fetchall()
    
    if(len(res)==1 and res[0][2]==hsh):    
        dbcon.commit()
        dbcon.close()
        set_session(email,hsh)
        ID,correo,hsh,sexo,altura,peso,diametro_humero,diametro_femur,diametro_brazo_contraido,perimetro_pantorrilla,pliegue_biseps,pliegue_subescapular,pliegue_suprailiaco,registrado=res[0]
        if(registrado):
            return redirect("/dietas",302)
        return redirect("/perfil",302)
    
    dbcon.commit()
    dbcon.close()
    
    return redirect("/ingreso",302)

@app.route("/registro/",methods=["GET"])
def registro():
    return render_template("registro.html")

@app.route("/registro",methods=["POST"])
@app.route("/registro/",methods=["POST"])
def registroP():
    dbcon = sqlite3.connect("stayfit.db")
    dbex = dbcon.cursor()
    
    #revisar si existe alguno con dicho email
    email=request.form['email']
    dbex.execute("SELECT * FROM usuarios WHERE (correo=?)",[email])
    res=dbex.fetchall()

    if len(res)>0 or (request.form['pass1'] != request.form['pass2']): #abortar la operacion, recargar
        dbcon.commit()
        dbcon.close()
        
        return redirect("/registro",302)
    
    #make new user
    hsh=H(request.form['pass1'])
    dbex.execute("INSERT INTO usuarios (correo, hash) VALUES (?, ?);",(email,hsh))
    
    dbcon.commit()
    dbcon.close()
    
    set_session(email,hsh)
    
    return redirect("/perfil",302)


@app.route("/perfil",methods=["GET"])
@app.route("/perfil/",methods=["GET"])
def perfil():
    user,_=get_session()
    
    ID,correo,hsh,sexo,altura,peso,diametro_humero,diametro_femur,diametro_brazo_contraido,perimetro_pantorrilla,pliegue_biseps,pliegue_subescapular,pliegue_suprailiaco,registrado=_
    
    
    return render_template("perfil.html",username=user,l=_)


@app.route("/perfil",methods=["POST"])
@app.route("/perfil/",methods=["POST"])
def perfilP():
    user,_=get_session()
    
    sexo,altura,peso,diametro_humero,diametro_femur,diametro_brazo_contraido,perimetro_pantorrilla,pliegue_biseps,pliegue_subescapular,pliegue_suprailiaco,registrado=[
        request.form['sexo'],
        request.form['altura'],
        request.form['peso'],
        request.form['femur'],
        request.form['humer'],
        request.form['arm'],
        request.form['calf'],
        request.form['bicep'],
        request.form['subesc'],
        request.form['supra'],
        True
    ]
    
    dbcon = sqlite3.connect("stayfit.db")
    dbex = dbcon.cursor()
    
    dbex.execute("UPDATE usuarios SET sexo=?,altura = ?,peso = ?,diametro_humero = ?,diametro_femur = ?,diametro_brazo_contraido = ?,perimetro_pantorrilla = ?,pliegue_biseps = ?,pliegue_subescapular = ?,pliegue_suprailiaco = ?,registrado = ? WHERE correo=?",[sexo,altura,peso,diametro_humero,diametro_femur,diametro_brazo_contraido,perimetro_pantorrilla,pliegue_biseps,pliegue_subescapular,pliegue_suprailiaco,registrado,user])
    
    dbcon.commit()
    dbcon.close()
    
    
    return redirect("/dietas",302)
    

@app.route("/dietas/")
def dietas():
    user,_=get_session()
    
    ID,correo,hsh,sexo,altura,peso,diametro_humero,diametro_femur,diametro_brazo_contraido,perim_pantorrilla,pliegue_bisep,pliegue_subescapular,pliegue_suprailiaco,registrado=_
    
    raiz_cubica_del_peso = peso**(1./3.)
    ip = altura / raiz_cubica_del_peso
    resultado_ecto = 0

    if ip >= 40.75:
        resultado_ecto = (0.732*ip) - 28.58
    elif ip >= 38.25 and ip <= 40.74:
        resultado_ecto = (0.463*ip) - 17.63
    elif ip < 38.24:
        resultado_ecto = 0.1

    perim_brazo_contraido = 28
    pliegue_pantorrilla = 14.3
    
    operacion1 = 0
    resultado_meso = 0

    resultado_meso = 0.858*diametro_humero + 0.601*diametro_femur + 0.188*(perim_brazo_contraido-pliegue_bisep) + 0.161*(perim_pantorrilla-pliegue_pantorrilla)

    '''Endomorfia'''

    operacion1 = (pliegue_bisep + pliegue_subescapular + pliegue_suprailiaco) * (170.18/altura)
    resultado_endo = (-0.7182 + (0.1451 * operacion1)) - (0.00068*operacion1**2) + 0.0000014*operacion1**3 
   
    
    if(resultado_ecto>resultado_meso and resultado_ecto>resultado_endo):
        return render_template("dietas.html",username=user,diet="\static\images\ecto.jfif")
    if(resultado_meso>resultado_ecto and resultado_meso>resultado_endo):
        return render_template("dietas.html",username=user,diet="\static\images\meso.jfif")
    if(resultado_endo>resultado_meso and resultado_endo>resultado_ecto):
        return render_template("dietas.html",username=user,diet="\static\images\endo.jfif") 
    
@app.route("/logout/")
def logout():
    set_session(None,None) 
    return redirect("/",302)

def get_data(user):
    dbcon = sqlite3.connect("stayfit.db")
    dbex = dbcon.cursor()

    dbex.execute("SELECT * FROM usuarios WHERE (correo=?)",[user])
    res=dbex.fetchall()
    if(res):
        res=res[0]

    dbcon.commit()
    dbcon.close()
    
    return res
    
def get_session():
    if 'user' in session:
        return session['user'], get_data(session['user'])
    return None,None

def set_session(email,hsh):
    session['user']=email
    session['hash']=hsh
    

def H(x):
    return hashlib.md5(x.encode("ascii")).hexdigest()

def set_db():
    dbcon = sqlite3.connect("stayfit.db")
    dbex = dbcon.cursor()
    
    dbex.execute("DROP TABLE IF EXISTS alimentos;")
    dbex.execute("DROP TABLE IF EXISTS usuarios;")
    dbex.execute("""create table usuarios(
id integer primary key autoincrement,
correo varchar(150) not null unique,
hash varchar(32) not null unique,

sexo boolean,
altura integer,
peso real,

diametro_humero real,
diametro_femur real,
diametro_brazo_contraido real,
perimetro_pantorrilla real,

pliegue_biseps real,
pliegue_subescapular real,
pliegue_suprailiaco real,

registrado boolean);""")
    
    dbex.execute("""create table alimentos(
nombre varchar(50) primary key not null,
tipo varchar(50) not null,
calorias int not null);""")
    
    dbex.execute('''INSERT INTO alimentos (nombre, tipo, calorias) VALUES
("Piña", "Fruta", 55),
("Albaricoque", "Fruta", 43),
("Pera", "Fruta", 55),
("Platano", "Fruta", 88),
("Arandanos", "Fruta", 35),
("Naranja roja", "Fruta", 45),
("Moras", "Fruta", 43),
("Arandanos rojos", "Fruta", 46),
("Fresas", "Fruta", 32),
("Higo", "Fruta", 107),
("Toronja", "Fruta", 50),
("Granada", "Fruta", 74),
("Melon", "Fruta", 54),
("Frambuesas", "Fruta", 36),
("Jengibre", "Fruta", 80),
("Kiwi", "Fruta", 51),
("Cerezas", "Fruta", 50),
("Lichi", "Fruta", 66),
("Mandarina", "Fruta", 50),
("Mango", "Fruta", 62),
("Maracuya", "Fruta", 97),
("Ciruela", "Fruta", 47),
("Melocoton", "Fruta", 41),
("Membrillo", "Fruta", 38),
("Ruibardo", "Fruta", 21),
("Sandia", "Fruta", 37),
("Uvas", "Fruta", 70),
("Limon", "Fruta", 35),

("Berenjena", "Verdura", 24),
("Alcachofa","Verdura",47),
("Aguacate","Verdura",160),
("Coliflor","Verdura",25),
("Brocoli","Verdura",35),
("Judias","Verdura",25),
("Berro de agua","Verdura",19),
("Champiñones","Verdura",22),
("Col china","Verdura",13),
("Guindilla","Verdura",40),
("Guisantes","Verdura",82),
("Lechuga iceberg","Verdura",14),
("Hinojo","Verdura",31),
("Pepino","Verdura",15),
("Col rizada","Verdura",49),
("Zanahoria","Verdura",36),
("Patata","Verdura",86),
("Colinabo","Verdura",27),
("Calabaza","Verdura",19),
("Puerro","Verdura",31),
("Maiz","Verdura",108),
("Acelgas","Verdura",19),
("Pimiento","Verdura",21),
("Rabanitos","Verdura",16),
("Remolacha","Verdura",43),
("Col lombarda","Verdura",29),
("Col de Bruselas","Verdura",43),
("Rula","Verdura",25),
("Esparragos","Verdura",18),
("Espinas","Verdura",23),
("Boniato","Verdura",76),
("Calabacin","Verdura",20),
("Cebolla","Verdura",40),

("Salchicha","Carne",375),
("Pato","Carne",192),
("Ciervo","Carne",94),
("Pechuga de pollo","Carne",75),
("Ternera","Carne",94),
("Cordero","Carne",178),
("Pechuga de pavo","Carne",111),
("Filete de cadera","Carne",162),
("Filete de vacuno","Carne",115),
("Carne picada de vacuno","Carne",212),
("Salami","Carne",507),
("Jamon cocido","Carne",335),
("Tocino","Carne",645),
("Filete de cerdo","Carne",191),
("Carne de cerdo, grasa","Carne",311),
("Carne de cerdo, magra","Carne",143),
("Solomillo de cerdo","Carne",105),
("Salchicha de Frankfurt","Carne",269),

("Tónica","Bebidas",34),
("Mate","Bebidas",15),
("Coca Cola","Bebidas",37),
("Fanta","Bebidas",37),
("Café","Bebidas",1),
("Cacao","Bebidas",398),
("Zumo multivitamínico","Bebidas",51),
("Leche de soja","Bebidas",36),

("Sardina","Pescado",50),
("Merluza","Pescado",50),
("Arenque","Pescado",146),
("Salmón","Pescado",137),
("Filete de perca","Pescado",111),
("Filete de abadejo","Pescado",83),
("Atún","Pescado",144),

("Suero de mantequilla","Lacteo",38),
("Arroz con leche","Lacteo",118),
("Chocolate caliente","Lacteo",89),
("Crema chantillí","Lacteo",266),
("Crema para café","Lacteo",195),
("Leche","Lacteo",61),
("Leche condensada","Lacteo",321),
("Leche entera","Lacteo",61),
("Yogur","Lacteo",61),
("Nata/Crema","Lacteo",242),
("Leche deslactosada","Lacteo",52),
("Leche en polvo","Lacteo",496),
("Leche evaporada","Lacteo",321),

("Fideos, cocidos","Pasta",142),
("Pasta de espelta, cocida","Pasta",128),
("Farfalle, cocidos","Pasta",157),
("Tallarines, cocidos","Pasta",159),
("Fideos chinos, cocidos","Pasta",109),
("Espagueti intengral, cocidos","Pasta",152);''')
    
    dbcon.commit()
    dbcon.close()
    

    return 0

if reset_db:
    set_db()

