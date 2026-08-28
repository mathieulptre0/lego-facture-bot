from datetime import datetime
import os
import discord
from discord import app_commands
from discord.ext import commands
import pymupdf as fitz

# ==========================================
# FONCTION DE GÉNÉRATION DU PDF
# ==========================================


def generer_ticket_pdf(
    nom_article,
    prix_article_str,
    date_valeur,
    date_lettre,
    heure_valeur,
    code_avis,
    tva_str,
):
  dossier = os.path.dirname(os.path.abspath(__file__))
  html_path = os.path.join(dossier, "page_blanche.html")
  pdf_path = os.path.join(dossier, "Receipt_generated.pdf")
  police_medium = os.path.join(dossier, "CeraProMedium.ttf")
  police_bold = os.path.join(dossier, "cera-pro-bold.ttf")
  image_avis_path = os.path.join(
      dossier, "73b318fc-9648-420d-b3f8-4728ee3156ee.png"
  )
  image_width200_path = os.path.join(dossier, "width200.png")
  image_width87_path = os.path.join(dossier, "width87.png")
  image_width60_path = os.path.join(dossier, "width60.png")
  image_width99_path = os.path.join(dossier, "width99.png")

  width_mm = 80
  height_mm = 385.8
  width_pt = width_mm / 25.4 * 72
  height_pt = height_mm / 25.4 * 72
  mediabox = fitz.Rect(0, 0, width_pt, height_pt)

  if os.path.exists(html_path):
    with open(html_path, encoding="utf-8") as f:
      html = f.read()
    archive = fitz.Archive(dossier)
    story = fitz.Story(html=html, archive=archive)
  else:
    story = None

  writer = fitz.DocumentWriter(pdf_path)
  dev = writer.begin_page(mediabox)
  if story:
    more = True
    while more:
      more, _ = story.place(mediabox)
      story.draw(dev)
  writer.end_page()
  writer.close()

  doc = fitz.open(pdf_path)
  page = doc[0]

  font_medium = fitz.Font(fontfile=police_medium)
  font_bold = fitz.Font(fontfile=police_bold)

  # Duplicata haut
  texte_duplicata_haut = "DUPLICATA"
  taille_dh = 15
  espacement_dh = -0.394
  left_pt_dh = 24 / 25.4 * 72
  top_pt_dh = 1 / 25.4 * 72
  page.insert_font(fontname="CeraBoldHaut", fontfile=police_bold)
  x, y = left_pt_dh, top_pt_dh + taille_dh
  for c in texte_duplicata_haut:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldHaut",
        fontsize=taille_dh,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=taille_dh) + espacement_dh

  # Image width60
  largeur_w60_pt = 19 / 25.4 * 72
  top_w60_pt = 15.3 / 25.4 * 72
  left_w60_pt = 28 / 25.4 * 72
  img_w60_doc = fitz.open(image_width60_path)
  hauteur_w60_pt = (
      largeur_w60_pt
      * img_w60_doc[0].rect.height
      / img_w60_doc[0].rect.width
  )
  page.insert_image(
      fitz.Rect(
          left_w60_pt,
          top_w60_pt,
          left_w60_pt + largeur_w60_pt,
          top_w60_pt + hauteur_w60_pt,
      ),
      filename=image_width60_path,
  )

  # Adresse LQT
  texte_lqt = "149 LEGO, LQT Paris, EU-FR"
  taille_lqt = 7.9
  espacement_lqt = 0.03
  x, y = 20 / 25.4 * 72, (40.4 / 25.4 * 72) + taille_lqt
  page.insert_font(fontname="CeraMediumLQT", fontfile=police_medium)
  for c in texte_lqt:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLQT",
        fontsize=taille_lqt,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_lqt) + espacement_lqt

  texte_adr2 = "15 Parv. de la Défense,"
  x, y = 23 / 25.4 * 72, (43.2 / 25.4 * 72) + 7.9
  page.insert_font(fontname="CeraMedium2", fontfile=police_medium)
  for c in texte_adr2:
    page.insert_text(
        (x, y), c, fontname="CeraMedium2", fontsize=7.9, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=7.9)

  texte_adr3 = "92092 Puteaux, FR"
  x, y = 25.5 / 25.4 * 72, (46.2 / 25.4 * 72) + 7.9
  page.insert_font(fontname="CeraMedium3", fontfile=police_medium)
  for c in texte_adr3:
    page.insert_text(
        (x, y), c, fontname="CeraMedium3", fontsize=7.9, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=7.9)

  texte_trans = "Transaction de vente"
  x, y = 11 / 25.4 * 72, (54.5 / 25.4 * 72) + 15
  page.insert_font(fontname="CeraBoldTrans", fontfile=police_bold)
  for c in texte_trans:
    page.insert_text(
        (x, y), c, fontname="CeraBoldTrans", fontsize=15, color=(0, 0, 0)
    )
    x += font_bold.text_length(c, fontsize=15)

  # Article dynamique
  taille_article = 9.5
  x, y = 2 / 25.4 * 72, (66 / 25.4 * 72) + taille_article
  page.insert_font(fontname="CeraMediumArt1", fontfile=police_medium)
  for c in nom_article:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumArt1",
        fontsize=taille_article,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_article)

  # Prix article dynamique
  right_pt_p1 = 72.5 / 25.4 * 72
  top_pt_p1 = 66 / 25.4 * 72
  page.insert_font(fontname="CeraMediumPrix1", fontfile=police_medium)
  largeur_totale_p1 = sum(
      font_medium.text_length(c, fontsize=9.5) for c in prix_article_str
  )
  x = right_pt_p1 - largeur_totale_p1
  y = top_pt_p1 + 9.5
  for c in prix_article_str:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumPrix1",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  texte_tva_taux = "Récapitulatif TVA  Taux"
  x, y = 2.2 / 25.4 * 72, (73.6 / 25.4 * 72) + 9.3
  page.insert_font(fontname="CeraMediumTVA", fontfile=police_medium)
  for c in texte_tva_taux:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVA",
        fontsize=9.3,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.3)

  texte_tva_seul = "TVA"
  x, y = 66.5 / 25.4 * 72, (73.7 / 25.4 * 72) + 9.2
  page.insert_font(fontname="CeraMediumTVATexte", fontfile=police_medium)
  for c in texte_tva_seul:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVATexte",
        fontsize=9.2,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.2)

  texte_20 = "20.0%"
  x, y = 30.8 / 25.4 * 72, (77.8 / 25.4 * 72) + 9.3
  page.insert_font(fontname="CeraMedium20", fontfile=police_medium)
  for c in texte_20:
    page.insert_text(
        (x, y), c, fontname="CeraMedium20", fontsize=9.3, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=9.3)

  right_pt_1e_nouveau = 72.7 / 25.4 * 72
  top_pt_1e_nouveau = 77.6 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumMontantTVA2", fontfile=police_medium
  )
  largeur_totale_1e_nov = sum(
      font_medium.text_length(c, fontsize=9.5) for c in tva_str
  )
  x = right_pt_1e_nouveau - largeur_totale_1e_nov
  y = top_pt_1e_nouveau + 9.5
  for c in tva_str:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantTVA2",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  texte_tot_label = "Total"
  x, y = 30.8 / 25.4 * 72, (81.5 / 25.4 * 72) + 9.3
  page.insert_font(
      fontname="CeraMediumTotalLabel", fontfile=police_medium
  )
  for c in texte_tot_label:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalLabel",
        fontsize=9.3,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.3)

  right_pt_1e = 72.6 / 25.4 * 72
  top_pt_1e = 81.4 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumTotalMontant", fontfile=police_medium
  )
  largeur_totale_1e = sum(
      font_medium.text_length(c, fontsize=9.5) - 0.02 for c in tva_str
  )
  x = right_pt_1e - largeur_totale_1e
  y = top_pt_1e + 9.5
  for c in tva_str:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalMontant",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5) - 0.02

  texte_nb = "Nombre d'articles : 1"
  x, y = 2.2 / 25.4 * 72, (91 / 25.4 * 72) + 9.5
  page.insert_font(
      fontname="CeraMediumNbArticles", fontfile=police_medium
  )
  for c in texte_nb:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumNbArticles",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  texte_tap = "Total à payer"
  x, y = 2.1 / 25.4 * 72, (96.5 / 25.4 * 72) + 11
  page.insert_font(
      fontname="CeraBoldTotalPayer", fontfile=police_bold
  )
  for c in texte_tap:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTotalPayer",
        fontsize=11,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=11) - 0.1

  right_pt_tp = 73 / 25.4 * 72
  top_pt_tp = 96.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraBoldPrixPayer", fontfile=police_bold
  )
  largeur_totale_tp = sum(
      font_bold.text_length(c, fontsize=11) for c in prix_article_str
  )
  x = right_pt_tp - largeur_totale_tp
  y = top_pt_tp + 11
  for c in prix_article_str:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldPrixPayer",
        fontsize=11,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=11)

  texte_paye = "Payé avec Visa"
  x, y = 2.1 / 25.4 * 72, (106.5 / 25.4 * 72) + 9.5
  page.insert_font(fontname="CeraMediumVisa", fontfile=police_medium)
  for c in texte_paye:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumVisa",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  right_pt_599e = 72.8 / 25.4 * 72
  top_pt_599e = 106.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumMontantVisa", fontfile=police_medium
  )
  largeur_totale_599e = sum(
      font_medium.text_length(c, fontsize=9.5) for c in prix_article_str
  )
  x = right_pt_599e - largeur_totale_599e
  y = top_pt_599e + 9.5
  for c in prix_article_str:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantVisa",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  largeur_img_pt = 74 / 25.4 * 72
  left_img_pt = 0.6 / 25.4 * 72
  top_img_pt = 120.3 / 25.4 * 72
  img_doc = fitz.open(image_avis_path)
  hauteur_img_pt = (
      largeur_img_pt * img_doc[0].rect.height / img_doc[0].rect.width
  )
  page.insert_image(
      fitz.Rect(
          left_img_pt,
          top_img_pt,
          left_img_pt + largeur_img_pt,
          top_img_pt + hauteur_img_pt,
      ),
      filename=image_avis_path,
  )

  largeur_w99_pt = 14 / 25.4 * 72
  left_w99_pt = 23.7 / 25.4 * 72
  top_w99_pt = 124.5 / 25.4 * 72
  img_w99_doc = fitz.open(image_width99_path)
  hauteur_w99_pt = (
      largeur_w99_pt
      * img_w99_doc[0].rect.height
      / img_w99_doc[0].rect.width
  )
  page.insert_image(
      fitz.Rect(
          left_w99_pt,
          top_w99_pt,
          left_w99_pt + largeur_w99_pt,
          top_w99_pt + hauteur_w99_pt,
      ),
      filename=image_width99_path,
  )

  texte_juger = "Comment jugez-"
  x, y = 39.8 / 25.4 * 72, (124.7 / 25.4 * 72) + 10.5
  page.insert_font(fontname="CeraBoldJuger", fontfile=police_bold)
  for c in texte_juger:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldJuger",
        fontsize=10.5,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.5)

  texte_vv = "vous votre"
  x, y = 39.8 / 25.4 * 72, (129 / 25.4 * 72) + 10.4
  page.insert_font(
      fontname="CeraBoldVousVotre", fontfile=police_bold
  )
  for c in texte_vv:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldVousVotre",
        fontsize=10.4,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.4)

  texte_exp = "expérience ?"
  x, y = 39.8 / 25.4 * 72, (133.2 / 25.4 * 72) + 10.4
  page.insert_font(
      fontname="CeraBoldExperience", fontfile=police_bold
  )
  for c in texte_exp:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldExperience",
        fontsize=10.4,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.4)

  texte_sinon = "Sinon, répondez en 3 minutes à notre"
  x, y = 23.6 / 25.4 * 72, (143.8 / 25.4 * 72) + 8
  page.insert_font(
      fontname="CeraMediumSinon", fontfile=police_medium
  )
  for c in texte_sinon:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumSinon",
        fontsize=8,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=8)

  texte_quest = "questionnaire sur LEGO.com/"
  x, y = 23.6 / 25.4 * 72, (146.5 / 25.4 * 72) + 8
  page.insert_font(
      fontname="CeraMediumQuestionnaire", fontfile=police_medium
  )
  for c in texte_quest:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumQuestionnaire",
        fontsize=8,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=8)

  texte_ss = "storesurvey"
  x, y = 23.5 / 25.4 * 72, (149.3 / 25.4 * 72) + 8
  page.insert_font(
      fontname="CeraMediumStoreSurvey", fontfile=police_medium
  )
  for c in texte_ss:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumStoreSurvey",
        fontsize=8,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=8)

  texte_besoin = "Au besoin, utilisez ce code :"
  x, y = 23.5 / 25.4 * 72, (154.2 / 25.4 * 72) + 8
  page.insert_font(
      fontname="CeraMediumAuBesoin", fontfile=police_medium
  )
  for c in texte_besoin:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAuBesoin",
        fontsize=8,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=8)

  x, y = 23.5 / 25.4 * 72, (157 / 25.4 * 72) + 8
  page.insert_font(
      fontname="CeraMediumCodeBesoin", fontfile=police_medium
  )
  for c in code_avis:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCodeBesoin",
        fontsize=8,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=8) + 0.25

  s1 = page.new_shape()
  s1.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 168 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 168 / 25.4 * 72),
  )
  s1.finish(color=(0, 0, 0), width=1)
  s1.commit()

  texte_ins_titre = "Deviens un LEGO® Insider !"
  x, y = 14 / 25.4 * 72, (170.8 / 25.4 * 72) + 10.5
  page.insert_font(fontname="CeraBoldInsider", fontfile=police_bold)
  for c in texte_ins_titre:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldInsider",
        fontsize=10.5,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.5)

  texte_ins1 = "Rejoins le programme LEGO® Insiders pour"
  x, y = 4 / 25.4 * 72, (177.2 / 25.4 * 72) + 9.7
  page.insert_font(
      fontname="CeraMediumInsider1", fontfile=police_medium
  )
  for c in texte_ins1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider1",
        fontsize=9.7,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.7) - 0.1

  texte_ins2 = "profiter de formidables avantages et"
  x, y = 8.8 / 25.4 * 72, (180.7 / 25.4 * 72) + 9.7
  page.insert_font(
      fontname="CeraMediumInsider2", fontfile=police_medium
  )
  for c in texte_ins2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider2",
        fontsize=9.7,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.7) - 0.1

  texte_ins3 = "récompenses LEGO®"
  x, y = 21.3 / 25.4 * 72, (184 / 25.4 * 72) + 9.7
  page.insert_font(
      fontname="CeraMediumInsider3", fontfile=police_medium
  )
  for c in texte_ins3:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider3",
        fontsize=9.7,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.7) - 0.1

  texte_ins_url = "LEGO.com/insiders"
  x, y = 22.2 / 25.4 * 72, (189 / 25.4 * 72) + 9.7
  page.insert_font(
      fontname="CeraMediumInsiderUrl", fontfile=police_medium
  )
  for c in texte_ins_url:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsiderUrl",
        fontsize=9.7,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.7) - 0.24

  s2 = page.new_shape()
  s2.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 196.2 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 196.2 / 25.4 * 72),
  )
  s2.finish(color=(0, 0, 0), width=1)
  s2.commit()

  texte_titre = "S'abonner aux e-mails"
  x, y = 18.3 / 25.4 * 72, (198.8 / 25.4 * 72) + 10.5
  page.insert_font(fontname="CeraBoldAbonner", fontfile=police_bold)
  for c in texte_titre:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldAbonner",
        fontsize=10.5,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.5)

  texte_l1 = "Suivez notre actualité en vous abonnant à"
  x, y = 4.8 / 25.4 * 72, (205.5 / 25.4 * 72) + 9.5
  page.insert_font(
      fontname="CeraMediumAbonner1", fontfile=police_medium
  )
  for c in texte_l1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAbonner1",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5) - 0.02

  texte_l2 = "notre programme d'e-mails LEGO.com/email"
  x, y = 2.5 / 25.4 * 72, (208.8 / 25.4 * 72) + 9.5
  page.insert_font(
      fontname="CeraMediumAbonner2", fontfile=police_medium
  )
  for c in texte_l2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAbonner2",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5) - 0.05

  s3 = page.new_shape()
  s3.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 216.2 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 216.2 / 25.4 * 72),
  )
  s3.finish(color=(0, 0, 0), width=1.3)
  s3.commit()

  texte_secu = "Caractéristiques de sécurité"
  x, y = 12.9 / 25.4 * 72, (218.8 / 25.4 * 72) + 10.5
  page.insert_font(fontname="CeraBoldSecurite", fontfile=police_bold)
  for c in texte_secu:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldSecurite",
        fontsize=10.5,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=10.5)

  largeur_w200_pt = 38.1 / 25.4 * 72
  left_w200_pt = 18.4 / 25.4 * 72
  top_w200_pt = 228.8 / 25.4 * 72
  img_w200_doc = fitz.open(image_width200_path)
  hauteur_w200_pt = (
      largeur_w200_pt
      * img_w200_doc[0].rect.height
      / img_w200_doc[0].rect.width
  )
  page.insert_image(
      fitz.Rect(
          left_w200_pt,
          top_w200_pt,
          left_w200_pt + largeur_w200_pt,
          top_w200_pt + hauteur_w200_pt,
      ),
      filename=image_width200_path,
  )

  s4 = page.new_shape()
  s4.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 293 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 293 / 25.4 * 72),
  )
  s4.finish(color=(0, 0, 0), width=1)
  s4.commit()

  page.insert_font(fontname="CeraBoldDuplicata", fontfile=police_bold)
  page.insert_text(
      (2 / 25.4 * 72, (268.1 / 25.4 * 72) + 7.2),
      "Duplicata",
      fontname="CeraBoldDuplicata",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(
      fontname="CeraMediumDuplicataRef", fontfile=police_medium
  )
  page.insert_text(
      (2 / 25.4 * 72, (270.8 / 25.4 * 72) + 7.2),
      "1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286",
      fontname="CeraMediumDuplicataRef",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraMediumLNE", fontfile=police_medium)
  page.insert_text(
      (2 / 25.4 * 72, (273.1 / 25.4 * 72) + 7.2),
      "Système de caisse certifié LNE",
      fontname="CeraMediumLNE",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraMediumLegal1", fontfile=police_medium)
  page.insert_text(
      (6.5 / 25.4 * 72, (278.5 / 25.4 * 72) + 7.2),
      "LEGO BRAND RETAIL S.A.S est enregistré au Registre",
      fontname="CeraMediumLegal1",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraMediumLegal2", fontfile=police_medium)
  page.insert_text(
      (2.5 / 25.4 * 72, (281 / 25.4 * 72) + 7.2),
      "national des metteurs sur le marché des jeux et jouets sous",
      fontname="CeraMediumLegal2",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraMediumLegal3", fontfile=police_medium)
  page.insert_text(
      (20.8 / 25.4 * 72, (283.5 / 25.4 * 72) + 7.2),
      "le numéro FR214763_12TBLL.",
      fontname="CeraMediumLegal3",
      fontsize=7.2,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraBoldCBTitre", fontfile=police_bold)
  page.insert_text(
      (2 / 25.4 * 72, (295.2 / 25.4 * 72) + 10.5),
      "Ticket de carte bancaire",
      fontname="CeraBoldCBTitre",
      fontsize=10.5,
      color=(0, 0, 0),
  )

  page.insert_font(fontname="CeraMediumCBDate", fontfile=police_medium)
  page.insert_text(
      (2 / 25.4 * 72, (300.8 / 25.4 * 72) + 9.5),
      "Date/Heure",
      fontname="CeraMediumCBDate",
      fontsize=9.5,
      color=(0, 0, 0),
  )

  page.insert_font(
      fontname="CeraMediumCBValeurDate", fontfile=police_medium
  )
  page.insert_text(
      (40.8 / 25.4 * 72, (300.8 / 25.4 * 72) + 9.5),
      date_valeur,
      fontname="CeraMediumCBValeurDate",
      fontsize=9.5,
      color=(0, 0, 0),
  )

  infos_cb = [
      (
          "CeraMediumCBCarte",
          "CeraMediumCBNumero",
          "Carte",
          "**** 0777",
          304,
          2,
          59,
      ),
      (
          "CeraMediumCBTypeCarte",
          "CeraMediumCBVisa",
          "Type de carte",
          "Visa",
          307.2,
          2,
          66.6,
      ),
      (
          "CeraMediumCBTypeSaisie",
          "CeraMediumCBPuce",
          "Type de saisie",
          "Puce sans contact",
          310.8,
          2,
          44.7,
      ),
      (
          "CeraMediumCBAID",
          "CeraMediumCBAIDValeur",
          "AID",
          "A0000000031010",
          314.2,
          2,
          45.5,
      ),
      (
          "CeraMediumCBAutor",
          "CeraMediumCBAutorValeur",
          "Code d'autor.",
          "056013",
          317.3,
          2,
          62,
      ),
  ]
  for f1, f2, l_txt, v_txt, top_m, x1_m, x2_m in infos_cb:
    page.insert_font(fontname=f1, fontfile=police_medium)
    page.insert_text(
        (x1_m / 25.4 * 72, (top_m / 25.4 * 72) + 9.5),
        l_txt,
        fontname=f1,
        fontsize=9.5,
        color=(0, 0, 0),
    )
    page.insert_font(fontname=f2, fontfile=police_medium)
    page.insert_text(
        (x2_m / 25.4 * 72, (top_m / 25.4 * 72) + 9.5),
        v_txt,
        fontname=f2,
        fontsize=9.5,
        color=(0, 0, 0),
    )

  s5 = page.new_shape()
  s5.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 324.8 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 324.8 / 25.4 * 72),
  )
  s5.finish(color=(0, 0, 0), width=1.3)
  s5.commit()

  largeur_w87_pt = 13.8 / 25.4 * 72
  left_w87_pt = 59 / 25.4 * 72
  top_w87_pt = 328 / 25.4 * 72
  img_w87_doc = fitz.open(image_width87_path)
  hauteur_w87_pt = (
      largeur_w87_pt
      * img_w87_doc[0].rect.height
      / img_w87_doc[0].rect.width
  )
  page.insert_image(
      fitz.Rect(
          left_w87_pt,
          top_w87_pt,
          left_w87_pt + largeur_w87_pt,
          top_w87_pt + hauteur_w87_pt,
      ),
      filename=image_width87_path,
  )

  page.insert_font(
      fontname="CeraBoldDetailsCommande", fontfile=police_bold
  )
  page.insert_text(
      (2 / 25.4 * 72, (327.3 / 25.4 * 72) + 10.5),
      "Détails de la commande",
      fontname="CeraBoldDetailsCommande",
      fontsize=10.5,
      color=(0, 0, 0),
  )

  details_cmd = [
      (
          "CeraMediumDetailsTransaction",
          "CeraMediumDetailsTransactionValeur",
          "Transaction n°:",
          "LEGO0064863689",
          332.8,
          30.5,
      ),
      (
          "CeraMediumDetailsDateLabel",
          "CeraMediumDetailsDateValeur",
          "Date et heure:",
          date_lettre,
          335.3,
          30.5,
      ),
  ]
  for f1, f2, l_txt, v_txt, top_m, x_val in details_cmd:
    page.insert_font(fontname=f1, fontfile=police_medium)
    page.insert_text(
        (2 / 25.4 * 72, (top_m / 25.4 * 72) + 8),
        l_txt,
        fontname=f1,
        fontsize=8,
        color=(0, 0, 0),
    )
    page.insert_font(fontname=f2, fontfile=police_medium)
    page.insert_text(
        (x_val / 25.4 * 72, (top_m / 25.4 * 72) + 8),
        v_txt,
        fontname=f2,
        fontsize=8,
        color=(0, 0, 0),
    )

  page.insert_font(
      fontname="CeraMediumDetailsHeureValeur", fontfile=police_medium
  )
  page.insert_text(
      (30.4 / 25.4 * 72, (338.2 / 25.4 * 72) + 8),
      heure_valeur,
      fontname="CeraMediumDetailsHeureValeur",
      fontsize=8,
      color=(0, 0, 0),
  )

  s6 = page.new_shape()
  s6.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 345 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 345 / 25.4 * 72),
  )
  s6.finish(color=(0, 0, 0), width=1)
  s6.commit()

  garanties = [
      (
          "CeraMediumGarantieL1",
          "Ce bien bénéficie auprès du vendeur d’une garantie",
          3.3,
          347.8,
      ),
      (
          "CeraMediumGarantieL2",
          "légale de conformité d’une durée de deux ans à",
          6,
          350.8,
      ),
      (
          "CeraMediumGarantieL3",
          "compter de sa remise au consommateur.",
          10.7,
          353.5,
      ),
  ]
  for fname, g_txt, x_m, top_m in garanties:
    page.insert_font(fontname=fname, fontfile=police_medium)
    page.insert_text(
        (x_m / 25.4 * 72, (top_m / 25.4 * 72) + 8),
        g_txt,
        fontname=fname,
        fontsize=8,
        color=(0, 0, 0),
    )

  s7 = page.new_shape()
  s7.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 360.2 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 360.2 / 25.4 * 72),
  )
  s7.finish(color=(0, 0, 0), width=1.3)
  s7.commit()

  retails = [
      ("CeraMediumRetailL1", "LEGO Brand Retail SAS", 22.5, 365.8),
      ("CeraMediumRetailL2", "75 rue de Tocqueville,", 23.2, 368.8),
      ("CeraMediumRetailL3", "75017 Paris, FR", 28, 371.5),
      ("CeraMediumRetailL4", "FR 61752526178", 27.4, 374.2),
  ]
  for fname, r_txt, x_m, top_m in retails:
    page.insert_font(fontname=fname, fontfile=police_medium)
    page.insert_text(
        (x_m / 25.4 * 72, (top_m / 25.4 * 72) + 8),
        r_txt,
        fontname=fname,
        fontsize=8,
        color=(0, 0, 0),
    )

  meta = doc.metadata
  meta["title"] = "Receipt"
  doc.set_metadata(meta)
  doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
  doc.close()

  return pdf_path


# ==========================================
# INTERFACE DISCORD & BOUTONS
# ==========================================


class TicketDownloadView(discord.ui.View):

  def __init__(self, pdf_path: str):
    super().__init__(timeout=180)
    self.pdf_path = pdf_path

  @discord.ui.button(
      label="Create your receipt",
      style=discord.ButtonStyle.blurple,
      emoji="📄",
      custom_id="create_receipt_btn",
  )
  async def download_button_callback(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if os.path.exists(self.pdf_path):
      file = discord.File(self.pdf_path, filename="Receipt.pdf")
      await interaction.response.send_message(
          "Voici votre reçu de caisse !", file=file, ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "❌ Erreur : Le fichier PDF est introuvable.", ephemeral=True
      )


class ReceiptCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(
      name="setup_receipt",
      description="Affiche le panel d'initialisation des reçus",
  )
  async def setup_receipt(self, interaction: discord.Interaction):
    # Logique de footer robuste récupérée du code addcoin
    bot_avatar = (
        self.bot.user.display_avatar.url
        if self.bot.user
        else (interaction.client.user.display_avatar.url if interaction.client.user else None)
    )
    bot_name = (
        self.bot.user.name
        if self.bot.user
        else (interaction.client.user.name if interaction.client.user else "Bot")
    )
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
    footer_text = f"{bot_name} | {now_str}"

    embed = discord.Embed(
        title="Receipt Tool",
        description=(
            "Welcome to our **server's invoicing system**! ✨\n\nYou can"
            " **generate your receipt** using the **button below this"
            " message**. You will only need to provide a **few details** to"
            " **finalize the creation** of your receipt.\n\n🏛️ **Cost to create a"
            " receipt :**\nGenerating a receipt will **deduct 1 coin** from your"
            " **personal balance**. If you **don't have any coins** in your"
            " account, you can **open a ticket** at `# ticket` to order"
            " some!\n\nℹ️ Unfortunately, only the **French version** is"
            " currently available; our team will **soon** be making **other"
            " languages** available to you."
        ),
        color=discord.Color.from_str("#0058ff"),
    )

    if bot_avatar:
      embed.set_footer(text=footer_text, icon_url=bot_avatar)
    else:
      embed.set_footer(text=footer_text)

    dummy_pdf_path = generer_ticket_pdf(
        nom_article="Article par défaut",
        prix_article_str="5.99 €",
        date_valeur="28/08/2026",
        date_lettre="28 août 2026",
        heure_valeur="18:30",
        code_avis="1234",
        tva_str="1.00 €",
    )
    view = TicketDownloadView(dummy_pdf_path)

    await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
  await bot.add_cog(ReceiptCog(bot))