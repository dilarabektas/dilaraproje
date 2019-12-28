import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import datetime
import time
load_dotenv()

app = Flask(__name__)

app.secret_key = "Çok gizli bir key"
uri = os.getenv('MONGO_ATLAS_URI')
client = MongoClient(uri)
kullanici = client.filmler.uyeler
yorumlar=client.filmler.yorumlar

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/filmler')
def filmler():
  try:
   if session['eposta'] and session['ad'] is not None:
      return render_template('filmler.html')
   else:
      durum="Giriş Yapınız"
      return render_template('index.html',hata=durum)
  except :
      durum="Giriş Yapınız"
      return render_template('index.html',hata=durum)
@app.route('/yorum')
def yorum():
  if session['eposta'] and session['ad'] is not None:
        yapilacaklar = []
        for yap in yorumlar.find():
          yapilacaklar.append({"_id": str(yap['_id']), "ad": yap['ad'], "tarih": yap['tarih'],"yorum": yap['yorum']})
        
        return render_template('yorum.html',veri=yapilacaklar)
  else:
      durum="Giriş Yapınız"
      return render_template('index.html',hata=durum)   

@app.route('/yorumyap',methods=['POST'])
def yorumyap():
    if session['eposta'] and session['ad'] is not None:
      comments = request.form["comments"]
      ad=  session['ad']
      email=  session['eposta']
      tarih= time.strftime("%x")
      eklencek = { "ad": ad, "mail": email,"tarih":str(tarih),"yorum":comments }
      yorumlar.insert_one(eklencek)
      yapilacaklar = []
      for yap in yorumlar.find():
          yapilacaklar.append({"_id": str(yap['_id']), "ad": yap['ad'], "tarih": yap['tarih'],"yorum": yap['yorum']})
        
      return render_template('yorum.html',veri=yapilacaklar)
    else:
      durum="Giriş Yapınız"
      return render_template('index.html',hata=durum)   

@app.route('/cikisyap',methods=['GET', 'POST'])
def cikisyap():
    session.pop('eposta', None)
    session.pop('ad', None)
    return redirect('/')




@app.route('/girisyap',methods=['GET', 'POST'])
def girisyap():
  if request.method == 'POST':
        # index.html formundan isim gelecek
        mail = request.form["email"]
        parola = request.form["parola"]
        veritabani=kullanici.find_one({"mail": mail})
        # epostaya ait olan kullanıcı var
        if   veritabani is not  None :
          if parola == veritabani.get('parola'):
            # şifre de eşleşiyorsa giriş başarılıdır
            # kullanıcının epostasını session içine al
            session['eposta'] = mail
            session['ad'] =  veritabani.get('ad')
            # todo ekleyebileceği sayfaya yönlendiriyoruz.
            return redirect('/filmler')
          else:
            durum="Hatalı şifre girdiniz"
            return render_template('index.html',hata=durum)
        else:
            durum="Hatalı email girdiniz"
            return render_template('index.html',hata=durum)
  else: 
    return redirect('/')

@app.route('/kaydol',methods=["POST"])
def kaydol():
  if request.method == 'POST':
        # index.html formundan isim gelecek
        ad = request.form["ad"]
        mail = request.form["email"]
        parola = request.form["parola"]
        eklencek = { "ad": ad, "mail": mail ,"parola":parola}
        u = kullanici.find_one({'mail':mail})
        if u is None :
                session['eposta'] = mail
                session['ad'] = ad
                x = kullanici.insert_one(eklencek)
                return redirect('/filmler')
        else:
            durum="eposta adresi daha önceden sistemde kayıtlı"
            return render_template('index.html',hata=durum)
  return render_template('index.html')

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)
 