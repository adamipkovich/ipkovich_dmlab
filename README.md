# Dmlab Próbafeladat


## Feladat részletei

- Adatok beszerzése egy publikus forrásból: Használj egy nyilvánosan elérhető API-t vagy egy könnyen scrape-elhető weboldalt. Gyűjtsd az adatokat egy SQL vagy noSQL adatbázisba, amely jobban illik a kiválasztott adatszerkezethez. Az adatok lehetnek például tőzsdei árak, piactér hirdetések, helyi éttermek ebédmenüi – olyan forrást válassz, ami üzleti szempontból releváns.
- Adatok feldolgozása: Végezz az adatokon valamilyen hasznos műveletet, ami üzleti értékkel bírhat. Nem szükséges gépi tanulási modellt építened; inkább arra vagyunk kíváncsiak, hogyan elemzed a nyers adatokat és milyen információkat tudsz kinyerni belőlük. Például vizsgálhatod az árváltozásokat, trendeket vagy egy adott termékkategória keresleti ingadozásait.
- A megoldás publikálása: A megoldásod tedd lokálisan használhatóvá frontend alkalmazás vagy REST API formájában, ahol az eredmények könnyen hozzáférhetők. A frontend lehet egy egyszerű dashboard vagy interaktív webes felület, míg az API biztosítson lehetőséget a feldolgozott adatok lekérdezésére és az eredmények visszaadására.


## Technikai követelmények

Programozási nyelv: A feladatot olyan programozási nyelven oldd meg, amelyben komfortosan dolgozol, bár a Python előnyt jelent számunkra.

Architektúra: A megoldás alapja legyen microservice architektúra, amely modularizálja az adatgyűjtési, feldolgozási és publikálási lépéseket.

Kipróbálhatóság: Fontos feltétel, hogy az elkészült kódod lokálisan kipróbálható legyen. Kérjük, biztosítsd, hogy minden szükséges leírás és konfiguráció elérhető legyen a GitHub-on.

Dokumentálás. Kérünk, hogy a munkád alapszinten dokumentáld. Néhány szóban írd le, hogy miért az adott probléma megoldását választottad, miért az adott technológiákkal dolgoztál, a megoldásod főbb részeinek működését.

# Megoldás

## Setup

A projekt lokálisan futtatható, felállítottam egy poetry környezetet, hogy könnyen telepíthető legyen az összes csomag. Ez azért is fontos, hogy Ti is ugyanolyan verziójú csomagokat használjatok.

```commandline
poetry install
```


## API lehívás

A feladat során IBM HR adatait használom. Ezt a [kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data)-ről töltöm le a saját API-jukkal. Azért ezt választottam, mert a munkavállalók megtartása kiemelten fontos a cégek számára, mert új alkalmazottakat be kell tanítani, sokszor olyan infrastruktúrában kell dolgozniuk, amit nem ismernek, így sokkal nagyob kockázatot jelentenek. Emiatt úgy gondoltam, hogy érdemes megvizsgálni azt, hogy melyek azok a válzotók, amelyekk leginkább hozzájárulnak a 

 Ennek feltétele, hogy saját kaggle fiókunk legyen. Biztonság miatt arra kérnélek, hogy csinálj Te is egy kaggle felhasználót majd a jöbb felső sarokban a profil képre kattintva étmegyünk a Settings részre, ahol az API-nál csinálhatunk access tokent. Amennyiben ezt nem szívesen csinálod meg, e-mailben mellékelem az én access tokenemet.

A letöltött .json file-t kérlek ide másold: C:\Users\<Your Username>\.kaggle\
Feltéve hogy windowsod van.

Valahogy így néz ki:
![alt text](assets/kaggle.png)

Van egy nagyon jó magyarázat hogyan lehet kaggle-ről adatsorokat letölteni, ezt [itt](https://medium.com/@vinaychavda.de/a-guide-to-extracting-data-from-kaggle-for-your-data-science-projects-e15ef8ffc054) találod.


IBM HR data 

A *data_request.py* fileban egy teszt található, aminél letölti a rendszer egy temp mappába egy beadott kaggle adatbázist (akár több .csv-vel rendelkező), majd beolvassa a kicsomagolt csv-ket a memóriába. Ezután ezt elmenti az adatbázisba, majd teszteli, hogy lekérhető-e az adat.

## Adattárolás

A feladat kifejezetten kéri a microservice architektúrát, ezért postgresql-t használok Docker Hubbal.

Ennek futtatásához szükség van a Docker-re és a [dockerhub](https://hub.docker.com/)-ra. Az első lépés, hogy lehúzzuk a postgresql DB-jét a Docker Hubról!
Írjuk a terminálba, hogy:
```commandline
docker pull postgres
```

Létre kell hozni egy Docker volume-ot, hogy meg tudjuk tartani az adatsort (ez akkor lenne fontos, ha konstans adatok érkeznek).

```commandline
docker volume create postgres_data
```

Futtassuk a postgres containert:

```commandline
docker run --name hr_data -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 -v postgres_data:/var/lib/postgresql/data postgres
```
Ebben a példában az alap adatbázist használjuk bármiféle "security" nélkül. 

Ha minden jól ment, akkor a DockerHubon a következőt látod:
![alt text](assets/docker_hub.png)


Én pgadmint használok a fejlesztés során, megtalálhatod [itt](https://www.pgadmin.org/). Ezzel monitorozhatod a postgresql adatbázist.
https://www.dbvis.com/thetable/how-to-set-up-postgres-using-docker/

Két fontos mozzanata van: feltöltés (data_request.py-ben) az upload_to_db és pull_table.


## Modelling

...

jupyter elmagyarázza a lépéseket.

modelling.py -ben benne vannak a lépések


## Frontend

Streamlit-et választottam mert egyszerű dashboardot készíteni vele. Technikailag jobb lenne ha építenék egy FastAPI backendet modelltanításra, mlflow-t MLOPS-ra és VC-ra, de az nem fér bele az allokált időbe. 

-> pull data on startup
-> modelling.py -vel készítem a modellt az elején cache-ve
-> ábrákat helyben elkészítjük (cache-lve), lementjük a shap-ot

voila.


```commandline
streamlit run frontend.py
```

## Docker??


