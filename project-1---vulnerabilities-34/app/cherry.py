#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from posixpath import normpath
import cherrypy
import sqlite3
import string


os.system("python3 basededados.py") #para correr basededados.py

dir = os.path.dirname(os.path.abspath(__file__))
string = os.path.join(dir,'shop.db') #Path para aas bases de dados

conf = {
  "/":     { "tools.staticdir.root": dir },
  
  "/css":  { "tools.staticdir.on": True,
			 "tools.staticdir.dir": "css" },
  "/images": { "tools.staticdir.on": True,
			 "tools.staticdir.dir": "images" },
  "/jscript": { "tools.staticdir.on": True,
			 "tools.staticdir.dir": "jscript" }
}

current_username=""
current_password=""

class App():
    @cherrypy.expose
    def index(self):
        return open('index.html','r')
    @cherrypy.expose
    def showComments(self):
       with sqlite3.connect(string) as conn:
        comand = conn.execute("SELECT * FROM comments")
        data = comand.fetchall()
        out = ""

        for row in data:
            comentario = row[1]
            author = row[2]
            out += """      
							<div class="tela-login">
                                <div class="tela-autor">
                                  <h3> Autor: %s </h3> 
                                  <div class="tela-comentarios"
                                  <h3>  %s </h3>
                                  </div>
                                </div>
                            </div>
                            
						"""%(author,comentario)
        
        return open('coments.html','r').read().format(out)
                
    @cherrypy.expose
    def addComment(self,comment):
       
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM users WHERE user_id=?",[current_user])
            data = comand.fetchall()
            author = data[0][1]
        with sqlite3.connect(string) as conn:
            k=conn.execute("INSERT into comments(comment,author) values (?,?)",[comment, author])
        return open('shop.html','r').read()

    @cherrypy.expose
    def addUser(self,user,password,password2):
        
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM users WHERE user=?",[user])
            data = comand.fetchall()
            if data!=[]:
                linha = """
							<p>Nome de utilizador já existe.Tente outra vez.</p>
							
                            
					"""    
                return open('passError.html','r').read().format(linha) #utilizador já existe
            if password == password2:
                comand=conn.execute("INSERT into users(user,password,balance) values (?,?,?)",[user, password, 0])
        return open('index.html','r').read() 
        
    

    @cherrypy.expose
    def shop(self,user=current_username,password=current_password):
        global current_user
        global current_username
        global current_password
        if user=="" and password=="":
            user = current_username
            password = current_password
        with sqlite3.connect(string) as conn:
            x = "SELECT * FROM users WHERE user= '" + user + "'  AND password='" + password + "'"
            
            comand = conn.execute(x,[]) #check if user exists in shop.db
            data = comand.fetchall()
            
            if data!=[]: 
                
                current_user = data[0][0]  # guarda o id do utilizador que fez login
                current_username=data[0][1]
                current_password = data[0][2]
                return open('shop.html','r').read()
            else :
                
                linha = """
							<p>User ou password inválido. Tente outra vez.</p>
							
                            
						"""
                return open('indexErro.html','r').read().format(linha)

    @cherrypy.expose
    def password(self):
        return open('password.html','r').read()

    @cherrypy.expose
    def reclamacao(self):
        return open('reclamacoes.html','r').read()
    
    @cherrypy.expose
    def sendReport(self,ficheiro):
       
        dir = os.path.dirname(__file__)
        nome = ficheiro.filename
        if nome == '':
            out = """
				<p>Submissão falhada. Ficheiro submetido não existe.</p>
							
                            
			"""
            return open('reclamacoes_out.html','r').read().format(out)
        f = os.path.normpath(os.path.join(dir,nome))
        with sqlite3.connect(string) as conn:
            comand = conn.execute("INSERT into files (user,file) values(?,?)",[current_user,nome])
        with open(f,'wb') as out:
            while True:
                aux = ficheiro.file.read(8192)
                if not aux:
                    break
                out.write(aux)
        out = """
				<p>Submissão concluída</p>
							
                            
			"""
    
						
        
        return open('reclamacoes_out.html','r').read().format(out)

    @cherrypy.expose
    def alterar_senha(self,user_name,last_password,new_password):
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM users WHERE user =?",[user_name])
            data = comand.fetchall()
            if data == []:
                linha = """
							<p>Utilizador ou password errada.</p>
							
                            
					"""   
                return open('passwordAlterada.html','r').read().format(linha)
            user_balance = data[0][3]
        with sqlite3.connect(string) as conn:
            r = conn.execute("REPLACE into users(user_id,user,password,balance) values (?,?,?,?)",[data[0][0],user_name,new_password,user_balance])
            linha = """
							<p>Password alterada com sucesso.</p>
							
                            
					"""    
        return open('passwordAlterada.html','r').read().format(linha)
        
    @cherrypy.expose
    def addProduct(self,product,quantity):
        
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM products WHERE name=?",[product])
            data = comand.fetchall()
            product_id = data[0][0]
            price = data[0][2]
            comand = conn.execute("SELECT * FROM orders WHERE product=? AND client=?",[product_id,current_user])
            data = comand.fetchall()
            if data!=[]:
                quantidade = data[0][3] + abs(int(quantity))
            else:
                quantidade=abs(int(quantity))    
            
            comand = conn.execute("REPLACE into orders(client,product,quantity) values (?,?,?)",[current_user,product_id,quantidade])  
            comand = conn.execute("SELECT * FROM users WHERE user_id=?",[current_user])
            data = comand.fetchall()
            balance=data[0][3]
            balance=balance+(price*-1)*(int(quantity)) # multiplicado por -1 para subtrair o saldo aquando da compra
            comand = conn.execute("UPDATE users SET balance = ? WHERE user_id = ?",[balance,current_user])  
            return open('shop.html','r').read() 

   
    @cherrypy.expose
    def showProducts(self):
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM orders WHERE client=?",[current_user])
            data = comand.fetchall()
            out = ""
            
        with sqlite3.connect(string) as conn:

            for row in data:
                product_id = row[2]
                quantity = row[3]
                with sqlite3.connect(string) as conn:
                    comand = conn.execute("SELECT * FROM products WHERE product_id=?",[product_id])
                    l = comand.fetchall()
                    for row in l:
                        product = row[1]
                        out += """      
                                        
                                            <h3> Produto: %s </h3> 
                                            
                                            <h3>  %s </h3>
                                            
                                        
                                        
                                    """%(product,quantity)
        with sqlite3.connect(string) as conn:
            comand = conn.execute("SELECT * FROM users WHERE user_id=?",[current_user])
            data = comand.fetchall()
            out1 = ""
            balance = data[0][3]
            out1 = """      
                                        
                                            <h3>  %s$ </h3> 
                                            
                                           
                                            
                                        
                                        
                                    """%(balance)
        return open('carrinho.html','r').read().format(out,out1)
        


if __name__ == '__main__':
    cherrypy.quickstart(App(),'/',conf)