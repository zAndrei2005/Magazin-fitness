--
-- PostgreSQL database dump
--

\restrict RsFApbLIP5XZ2D55GFnZI9mvlqhhjhZTvJDsjPBB7aNK9RantKmgzDoYWzgencG

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: aplicatie_brand; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_brand (id_brand, nume, tara_origine, website, an_infiintare) VALUES (1, 'GymShark', 'England', 'www.gymshark.com', 2000);
INSERT INTO django.aplicatie_brand (id_brand, nume, tara_origine, website, an_infiintare) VALUES (2, 'Stayfit', 'Romania', 'www.stayfit.ro', 2011);


--
-- Data for Name: aplicatie_categorie; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_categorie (id_categorie, nume, descriere, numar_produse, culoare, icon) VALUES (4, 'Accesorii fitness', 'Imbunatatesc experienta si eficienta la sala', 6, '#16a34a', 'fa-dumbbell');
INSERT INTO django.aplicatie_categorie (id_categorie, nume, descriere, numar_produse, culoare, icon) VALUES (3, 'Suplimente', 'Ajuta in parcursul progresului la sala, dar nu inlocuiesc o dieta alimentara echilibrata', 4, '#0ea5e9', 'fa-capsules');


--
-- Data for Name: aplicatie_culoare; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_culoare (id_culoare, nume, cod_hex, data_adaugare, intensitate) VALUES (1, 'Rosu', '#FF0000', '2025-11-05', 10);
INSERT INTO django.aplicatie_culoare (id_culoare, nume, cod_hex, data_adaugare, intensitate) VALUES (2, 'Albastru', '#0000FF', '2025-11-05', 8);
INSERT INTO django.aplicatie_culoare (id_culoare, nume, cod_hex, data_adaugare, intensitate) VALUES (3, 'Negru', '#000000', '2025-11-05', 10);
INSERT INTO django.aplicatie_culoare (id_culoare, nume, cod_hex, data_adaugare, intensitate) VALUES (4, 'Maro', '#964B00', '2025-11-05', 5);


--
-- Data for Name: aplicatie_dimensiune; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_dimensiune (id_dimensiune, eticheta, unitate_masura, disponibil, lungime, latime) VALUES (1, 'M', 'cm', true, 40.00, 40.00);
INSERT INTO django.aplicatie_dimensiune (id_dimensiune, eticheta, unitate_masura, disponibil, lungime, latime) VALUES (2, 'L', 'cm', true, 45.00, 45.00);


--
-- Data for Name: aplicatie_furnizor; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_furnizor (id_furnizor, nume, tara, email, telefon, rating) VALUES (1, 'GymBeam', 'Romania', 'gymbeam@gmail.com', '0712121212', 5);
INSERT INTO django.aplicatie_furnizor (id_furnizor, nume, tara, email, telefon, rating) VALUES (2, 'MyProtein', 'England', 'myprotein@gmail.com', '5551221121', 4);


--
-- Data for Name: aplicatie_locatie; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_locatie (id, adresa, oras, judet, cod_postal, nr) VALUES (1, 'Piata Ivancea', 'Curtea de Arges', 'Pitesti', '07123', 0);
INSERT INTO django.aplicatie_locatie (id, adresa, oras, judet, cod_postal, nr) VALUES (2, 'Strada Stefan cel Mare', 'Comuna Berceni', 'Ilfov', '123123', 0);


--
-- Data for Name: aplicatie_organizator; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_organizator (id, nume, email) VALUES (1, 'organizatorul 1', 'primul@gmail.com');
INSERT INTO django.aplicatie_organizator (id, nume, email) VALUES (2, 'organizatorul 2', 'doilea@gmail.com');


--
-- Data for Name: aplicatie_produs; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (1, 'Whey Protein Choco 1kg', 180.00, 'Supliment alimentar care ajuta formarea in masa musculara si in executarea de exercitii fizice intense. A se citi modul de utilizare!', true, '2025-11-05', 1, 3, 2);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (2, 'Whey Protein Choco 5kg', 350.00, 'Supliment alimentar care ajuta formarea in masa musculara si in executarea de exercitii fizice intense. A se citi modul de utilizare!', true, '2025-11-05', 1, 3, 2);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (3, 'Creatina Monohidrata 250g', 98.00, 'Supliment alimentar care ajuta formarea in masa musculara si in executarea de exercitii fizice intense. A se citi modul de utilizare!', true, '2025-11-05', 2, 3, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (4, 'Creatina Monohidrata 500g', 200.00, 'Supliment alimentar care ajuta formarea in masa musculara si in executarea de exercitii fizice intense. A se citi modul de utilizare!', true, '2025-10-14', 2, 3, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (5, 'Lifting Straps', 32.00, 'Accesorii ridicari greutati, perfect pentru antrenament intense dar si de agrement.', true, '2025-11-05', 2, 4, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (6, 'Lifting Straps', 32.00, 'Accesorii fitness pentru ridicat greutati, perfect pentru antrenamente intense dar si de agrement.', true, '2025-11-05', 2, 4, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (8, 'Tricou inscriptionat OLTEANU', 99.00, 'Cel mai tare tricou din lume la un pret accesibil', true, '2025-11-05', 2, 4, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (9, 'Tricou inscriptionat OLTEANU', 99.00, 'Cel mai tare tricou din lume la un pret accesibil', true, '2025-11-05', 2, 4, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (7, 'Lifting Belt', 55.00, 'Curea pentru ridicat greutati cu suport in zona abdominala', true, '2025-11-05', 2, 4, 1);
INSERT INTO django.aplicatie_produs (id_produs, nume, pret, descriere, stoc_disponibil, data_adaugare, brand_id, categorie_id, furnizor_id) VALUES (10, 'Lifting Belt', 55.00, 'Curea pentru ridicat greutati, se foloseste in zona abdominala si ofera stabilitate', true, '2025-11-05', 2, 4, 1);


--
-- Data for Name: aplicatie_produs_culori; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (1, 1, 2);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (2, 2, 2);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (3, 3, 1);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (4, 4, 1);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (5, 5, 3);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (6, 6, 3);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (7, 7, 4);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (8, 8, 3);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (9, 9, 3);
INSERT INTO django.aplicatie_produs_culori (id, produs_id, culoare_id) VALUES (10, 10, 4);


--
-- Data for Name: aplicatie_produs_dimensiuni; Type: TABLE DATA; Schema: django; Owner: andrei
--

INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (1, 1, 1);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (2, 2, 2);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (3, 3, 1);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (4, 4, 2);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (5, 5, 1);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (6, 6, 2);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (7, 7, 2);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (8, 8, 1);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (9, 9, 2);
INSERT INTO django.aplicatie_produs_dimensiuni (id, produs_id, dimensiune_id) VALUES (10, 10, 1);


--
-- Name: aplicatie_brand_id_brand_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_brand_id_brand_seq', 2, true);


--
-- Name: aplicatie_categorie_id_categorie_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_categorie_id_categorie_seq', 4, true);


--
-- Name: aplicatie_culoare_id_culoare_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_culoare_id_culoare_seq', 4, true);


--
-- Name: aplicatie_dimensiune_id_dimensiune_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_dimensiune_id_dimensiune_seq', 2, true);


--
-- Name: aplicatie_furnizor_id_furnizor_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_furnizor_id_furnizor_seq', 2, true);


--
-- Name: aplicatie_locatie_id_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_locatie_id_seq', 2, true);


--
-- Name: aplicatie_organizator_id_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_organizator_id_seq', 2, true);


--
-- Name: aplicatie_produs_culori_id_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_produs_culori_id_seq', 12, true);


--
-- Name: aplicatie_produs_dimensiuni_id_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_produs_dimensiuni_id_seq', 12, true);


--
-- Name: aplicatie_produs_id_produs_seq; Type: SEQUENCE SET; Schema: django; Owner: andrei
--

SELECT pg_catalog.setval('django.aplicatie_produs_id_produs_seq', 12, true);


--
-- PostgreSQL database dump complete
--

\unrestrict RsFApbLIP5XZ2D55GFnZI9mvlqhhjhZTvJDsjPBB7aNK9RantKmgzDoYWzgencG

