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
 
Python 3.12-vel dolgozom. [ITT](https://www.python.org/downloads/release/python-3127/) letöltheted. Vscode-ban dolgozom, a service-ket külön terminálban futtatom, a DB-n kívűl amit [docker](https://www.docker.com/)en keresztül futtatok.
A githubon a main branchen található a működő kód. Ezt kérlek egy git clone-nal húzd le.
A projekt lokálisan futtatható, felállítottam egy poetry környezetet, hogy könnyen telepíthető legyen az összes csomag. Ez azért is fontos, hogy Ti is ugyanolyan verziójú csomagokat használjatok.

```commandline
poetry install
```

A rendszer egy postgresql adatbázist, 2 microservice API-t és egy frontendnet tartalmaz és IBM HR adatbázisát dolgozza fel.

## Adattárolás

A feladat kifejezetten kéri a microservice architektúrát, ezért postgresql-t használok Dockerrel.

Ennek futtatásához szükség van a [Docker](https://hub.docker.com/)-re. Az első lépés, hogy lehúzzuk a postgresql DB-jét a Docker Hubról!
Írjuk a terminálba, hogy:
```commandline
docker pull postgres
```

Létrehozunk egy Docker volume-ot, hogy meg tudjuk tartani az adatsort leállítás után is (ez akkor lenne fontos, ha konstans adatok érkeznek).

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
A rendszer képes kezelni, ha esetleg több csv fájlt csomagolna le a kaggle. Jelen esetben ez 1.

Természetesen lehetne tovább bonyolítani, hogy kicseréljük az adatbázist (váltanánk pl. mysql-re). SQLalchemy-vel könnyen cserélhető, hasonló szintaxtist nyújt, csak egy új függvényt kell írni az engine-re.

## API lehívás

A feladat során IBM HR adatait használom. Ezt a [kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset/data)-ről töltöm le a saját API-jukkal. Azért ezt választottam, mert a munkavállalók megtartása kiemelten fontos a cégek számára, mert új alkalmazottakat be kell tanítani, sokszor olyan infrastruktúrában kell dolgozniuk, amit nem ismernek, így sokkal nagyobb kockázatot jelentenek. Emiatt úgy gondoltam, hogy érdemes megvizsgálni azt, hogy melyek azok a válzotók, amelyekk leginkább hozzájárulnak a 

Ennek feltétele, hogy saját kaggle fiókunk legyen. Biztonság miatt arra kérnélek, hogy csinálj Te is egy kaggle felhasználót majd a jöbb felső sarokban a profil képre kattintva étmegyünk a Settings részre, ahol az API-nál csinálhatunk access tokent. Amennyiben ezt nem opció, kérlek írjatok nekem, e-mailben mellékelem az én access tokenemet.

A letöltött .json file-t kérlek ide másold ha windowsod van: C:\Users\<Your Username>\.kaggle\

Linux/UNIX/OSX:
~/.kaggle/kaggle.json


Az access token lekérése itt található:
![alt text](assets/kaggle.png)


Van egy nagyon jó magyarázat hogyan lehet kaggle-ről adatsorokat letölteni, ezt [itt](https://medium.com/@vinaychavda.de/a-guide-to-extracting-data-from-kaggle-for-your-data-science-projects-e15ef8ffc054) találod.


A [data_request.py](data_request.py) fileban egy teszt található, aminél letölti a rendszer egy temp mappába egy beadott kaggle adatbázist (akár több .csv-vel rendelkező), majd beolvassa a kicsomagolt csv-ket a memóriába. Ezután ezt elmenti az adatbázisba, majd teszteli, hogy lekérhető-e az adat.

Kipróbálni a :
```commandline
python data_request.py
```
paranccsal lehet.

A [Collector Service](collector_service.py)-t egy uvicorn szerverrel futtatott FastAPI alapú REST API, aminek dolga letölteni a kaggle-ről az adatokat, és elküldeni az adatbázisba. Ami feltűnő lehet, hogy globális változóként adom meg a szerverhez szükséges adatot -> ez azért van, hogy ha docker image-ként akarnánk futtatni, később lehessen változtatni a docerk file-on, vagy a docker-compose-on bellül.

Tesztelni a microservice-t a [request_collection.py](request_collection.py)-vel lehet. Ez tulajdonképpen ugyan azt csinálja, mint a data_request, de requests könyvtárral, URL alapú post requestet kér a collector servicetől, hogy töltse fel az adatot az adatbázisba. Ezt a "/pull" post paranccsal tehetjük meg.
A szerver localhost 8015-ös portjára van konfigurálva. 

A futtatáshoz:
```commandline
python collector_service.py
```

## Modelling

A feladat egyszerű - szeretném megvizsgálni azt, hogy egyes munkavállalóknál mi az ami hozzátehet a kiégéshez/lemorzsolódáshoz (ami egy bináris klasszifikációs probléma). Ezért a draft_data_processing.ipynb-ban csináltam egy gyors xgboost klasszifikációs modelt, majd ennek a SHAP elemzését. Így individuálisan magyarázható, kinél mi volt a __MODEL!!!__ szerint lehetséges kiégést okozó faktor. Természetesen ez nem kauzalítás, és a modell vehet alapul olyan feltételezéseket, amelyek hamisak. Ezért mindig fontos tesztelni a kauzalítást, és kísérlettervezéssel célratörően megvizsgálni, hogy vajon tényleg ilyen mértékben befolyásolhatták-e a munkavállalókat a faktorok.
_______

A kategórikus változókat jóllehet nem dolgoztam fel teljesen, ezt tovább lehetne bonyolítani sklearn.preprocessing.LabelEncoder-rel. Az idő miatt ezt nem tettem meg, ez az analízisben a summary-ben szürke színként jelen majd meg.

Készítek egy korrelációs táblát, számos numerikus változó korrelál egymással. Confounding faktorok lehetnek az analízis során, de ez most nem lényeges.

GridSearch-csel készítek egy xgboost modelt. Azért válaszottam ezt a modelt mert:
- Gyors (párhuzamosítva és optimálva van, jól kezeli a tabuláris, nagy adattáblákat)
- Gyakran jobb eredményt ad mint egy szimpla random forest, vagy alap módszer
- Interpretabilítás nem lényeg (SHAP miatt)

Accuracy alapján tanítom a modellt, mert itt minden érték eltalálása számít.

Az analízis a SHAP módszeren alapul ami alapvetően a model interpretability problémájának megoldására lett kifejlesztve.  A SHAP kiszámolja az egyéni hozzáadott értékeket, és az értékek szummája a várható értéktől való eltérés. Ez egy kipróbált módszer és nagyon jó arra hogy megvizsgáljuk a modellünk miért döntött úgy ahogy. A shapley értékek tulajdonképpen alkalmazhatóak arra hogy munkavállaloknál egyes faktorok mennyire játszanak bele valakinek a lemorzsolódásába, de természetesen kiemelendő, hogy a modell szerint. Az ábrák könnyen értelmezhetőek szakértők számára, egy kis leírással pedig akár bárki értelmezheti őket.

[modelling.py](modelling.py)-ben függvényekké alakítottam a fontosabb lépéseket. Ebben szintúgy egy teszt található, amely egy SHAP beeswarm ábrát dob vissza. 
Ha ez nem fut le, valószínű nincs a DB-ben az adattábla.

[explainer_service.py](explainer_service.py) nagyon hasonló felépítése van mint A Collector Servicenek, de ez a microservice egy SHAP Explainer objektumot küldd vissza (adatok lekérését, lefuttatja a modelltanítást, és a SHAP-analízist). A post "/explain/{table_name}" parancs végrehajtja az analízist. Sajnos a table_name paraméter csak a "wa_fn_usec__hr_employee_attrition" érték lehet, mert ez egy célirányos elemzés, ugyanakkor ez a service bármikor cserélhető, amennyiben a post /explain-nek mindig egy pickled SHAP explainer objektum az eredménye. A Service funkcionalítását a [request_explanation.py](request_explanation.py) teszteli.  

Az uvicorn szerver localhost 8010-ös portjára van konfigurálva. 

A futtatáshoz:
```commandline
python explainer_service.py
```

## Frontend

Frontendnek a Streamlit-et választottam mert egyszerű dashboardot készíteni vele. Technikailag jobb lenne ha építenék egy FastAPI backendet modelltanításra, mlflow-t MLOPS-ra és VC-ra, de az nem fér bele az allokált időbe. Korrelációs mátrixot a draftban vizsgálok, de a dashboardba már nem került bele.

A frontend akkor működik, ha az össze többi service is fut, egyébként meg hibát/valamilyen információt fog adni, ha nem.

Futtassuk:
```commandline
streamlit run frontend.py
```

Végeredmény:
![alt text](assets/dashboard.png)

Ahol négy interaktálható elem van:
- "Pull Data from kaggle!" __gomb__ : Kéri a Collector Service-t  hogy töltse le az adatsort a kaggle-ről, feltölti a DB-be. Ezt annyiszor megteszi, ahányszor kérjük (lehet hogy egy másik adatbázis percenként frissül)!
- "Get explanation!" __gomb__ : Kéri az Explainer Service-t hogy az adatokra készítsen egy Explainer objektumot, majd küldje el a frontendnek. Ez jelenleg egyszer fut le (nagyon költséges modellt tanítani/explainer-t készíteni így limitáltam)
- Figure type __selectbox__ : Ez két fajta ábrázolást mutat - Summary, ami az egész adatbázist magyarázza, és az Individual-t ami pedig a munkavállalókat (mintákat) magyarázza.
- Employee number __selectbox__ : Csak a minták (figure type "Individual" opció) vizsgálatánál releváns. ID alapján kiválasztunk egy munkavállalót, és őt magyarázzuk.

Az ábrákat cache-elem, tehát nem kell egynél többször regenerálni. Elnézést kérek, hogy ha lassú a frontend, gyorsan oldottam meg a feladatot, és a microservice architektúra neméppen a legoptimálisabb egy ilyen "kicsi" feladat megoldásához.


## Docker

Sajnos erre nincs időm, de a kódokatúgy írtam meg, hogy Docker-rel és Docker Compose-zal egy teljes értékű applikáció készülhessen belőle. Ezért van a két service-nél globális változóban a postgresql credential. A frontendnél külön még be kell rakni a két service elérhetőségét egy állapotváltozóba, amelyet szintúgy egy globális változóként kezelhetünk.

