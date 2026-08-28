import os
import pymupdf as fitz


def executer_generation_complete(
    item_name="Porte-clés Miles Morales",
    item_price="5,99 €",
    tva_price="1,00 €",
    date_time="24/08/2026 19:35:15",
    date_long="24 août 2026",
    heure="19:35:15",
    code_besoin="149-64863689-08-24-2026 ",
):
  # Chemins des fichiers
  dossier = r"C:\Users\leazy\Desktop\lego facture bot"
  html_path = os.path.join(dossier, "page_blanche.html")
  pdf_path = os.path.join(dossier, "Receipt.pdf")
  police_medium = os.path.join(dossier, "CeraProMedium.ttf")
  police_bold = os.path.join(dossier, "cera-pro-bold.ttf")
  image_avis_path = os.path.join(
      dossier, "73b318fc-9648-420d-b3f8-4728ee3156ee.png"
  )
  image_width200_path = os.path.join(dossier, "width200.png")
  image_width87_path = os.path.join(dossier, "width87.png")
  image_width60_path = os.path.join(dossier, "width60.png")
  image_width99_path = os.path.join(dossier, "width99.png")

  # 1. --- Conversion HTML vers PDF ---
  width_mm = 80
  height_mm = 385.8

  width_pt = width_mm / 25.4 * 72
  height_pt = height_mm / 25.4 * 72
  mediabox = fitz.Rect(0, 0, width_pt, height_pt)

  with open(html_path, encoding="utf-8") as f:
    html = f.read()

  archive = fitz.Archive(dossier)
  story = fitz.Story(html=html, archive=archive)
  writer = fitz.DocumentWriter(pdf_path)

  more = True
  while more:
    dev = writer.begin_page(mediabox)
    more, _ = story.place(mediabox)
    story.draw(dev)
    writer.end_page()

  writer.close()

  doc = fitz.open(pdf_path)
  page = doc[0]

  font_medium = fitz.Font(fontfile=police_medium)
  font_bold = fitz.Font(fontfile=police_bold)

  # 2. --- Insertion du texte "DUPLICATA" (en haut) ---
  texte_duplicata_haut = "DUPLICATA"
  taille_dh = 15
  espacement_dh = -0.394
  left_mm_dh = 24
  top_mm_dh = 1
  left_pt_dh = left_mm_dh / 25.4 * 72
  top_pt_dh = top_mm_dh / 25.4 * 72

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

  # 3. --- Insertion de l'image (width60.png) ---
  largeur_w60_mm = 19
  left_w60_mm = 28
  top_w60_mm = 15.3
  left_w60_pt = left_w60_mm / 25.4 * 72
  top_w60_pt = top_mm_mm / 25.4 * 72  # Attention au nom de variable d'origine
  # Utilisation sécurisée des largeurs d'images d'origine :
  largeur_w60_pt = largeur_w60_mm / 25.4 * 72
  img_w60_doc = fitz.open(image_width60_path)
  ratio_w60 = img_w60_doc[0].rect.height / img_w60_doc[0].rect.width
  hauteur_w60_pt = largeur_w60_pt * ratio_w60
  rect_w60 = fitz.Rect(
      left_w60_pt,
      top_w60_pt,
      left_w60_pt + largeur_w60_pt,
      top_w60_pt + hauteur_w60_pt,
  )
  page.insert_image(rect_w60, filename=image_width60_path)

  # 4. --- Insertion du texte "149 LEGO, LQT Paris, EU-FR" ---
  texte_lqt = "149 LEGO, LQT Paris, EU-FR"
  taille_lqt = 7.9
  espacement_lqt = 0.03
  left_pt_lqt = 20 / 25.4 * 72
  top_pt_lqt = 40.4 / 25.4 * 72
  page.insert_font(fontname="CeraMediumLQT", fontfile=police_medium)
  x, y = left_pt_lqt, top_pt_lqt + taille_lqt
  for c in texte_lqt:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLQT",
        fontsize=taille_lqt,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_lqt) + espacement_lqt

  # 5. --- Insertion de la deuxième ligne d'adresse ---
  texte_adr2 = "15 Parv. de la Défense,"
  taille_adr2 = 7.9
  espacement_adr2 = 0
  left_pt_adr2 = 23 / 25.4 * 72
  top_pt_adr2 = 43.2 / 25.4 * 72
  page.insert_font(fontname="CeraMedium2", fontfile=police_medium)
  x, y = left_pt_adr2, top_pt_adr2 + taille_adr2
  for c in texte_adr2:
    page.insert_text(
        (x, y), c, fontname="CeraMedium2", fontsize=taille_adr2, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=taille_adr2) + espacement_adr2

  # 6. --- Insertion de la troisième ligne d'adresse ---
  texte_adr3 = "92092 Puteaux, FR"
  taille_adr3 = 7.9
  espacement_adr3 = 0
  left_pt_adr3 = 25.5 / 25.4 * 72
  top_pt_adr3 = 46.2 / 25.4 * 72
  page.insert_font(fontname="CeraMedium3", fontfile=police_medium)
  x, y = left_pt_adr3, top_pt_adr3 + taille_adr3
  for c in texte_adr3:
    page.insert_text(
        (x, y), c, fontname="CeraMedium3", fontsize=taille_adr3, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=taille_adr3) + espacement_adr3

  # 6 bis. --- Insertion du texte "Transaction de vente" ---
  texte_trans = "Transaction de vente"
  taille_trans = 15
  espacement_trans = 0
  left_pt_tr = 11 / 25.4 * 72
  top_pt_tr = 54.5 / 25.4 * 72
  page.insert_font(fontname="CeraBoldTrans", fontfile=police_bold)
  x, y = left_pt_tr, top_pt_tr + taille_trans
  for c in texte_trans:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTrans",
        fontsize=taille_trans,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=taille_trans) + espacement_trans

  # 7. --- Insertion de l'article (Dynamique) ---
  taille_article = 9.5
  espacement_article = 0
  left_pt_art = 2 / 25.4 * 72
  top_pt_art = 66 / 25.4 * 72
  page.insert_font(fontname="CeraMediumArt1", fontfile=police_medium)
  x, y = left_pt_art, top_pt_art + taille_article
  for c in item_name:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumArt1",
        fontsize=taille_article,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_article) + espacement_article

  # 8. --- Insertion du prix de l'article (Dynamique, aligné à droite) ---
  taille_p1 = 9.5
  espacement_p1 = 0
  right_pt_p1 = 72.5 / 25.4 * 72
  top_pt_p1 = 66 / 25.4 * 72
  page.insert_font(fontname="CeraMediumPrix1", fontfile=police_medium)
  largeur_totale_p1 = sum(
      font_medium.text_length(c, fontsize=taille_p1) + espacement_p1
      for c in item_price
  )
  x, y = right_pt_p1 - largeur_totale_p1, top_pt_p1 + taille_p1
  for c in item_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumPrix1",
        fontsize=taille_p1,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_p1) + espacement_p1

  # 9. --- Récapitulatif TVA Taux ---
  texte_tva_taux = "Récapitulatif TVA  Taux"
  taille_tva_taux = 9.3
  espacement_tva_taux = 0
  left_pt_tva = 2.2 / 25.4 * 72
  top_pt_tva = 73.6 / 25.4 * 72
  page.insert_font(fontname="CeraMediumTVA", fontfile=police_medium)
  x, y = left_pt_tva, top_pt_tva + taille_tva_taux
  for c in texte_tva_taux:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVA",
        fontsize=taille_tva_taux,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_tva_taux) + espacement_tva_taux

  # 9 bis. --- TVA ---
  texte_tva_seul = "TVA"
  taille_tva_seul = 9.2
  espacement_tva_seul = 0
  left_pt_tvas = 66.5 / 25.4 * 72
  top_pt_tvas = 73.7 / 25.4 * 72
  page.insert_font(fontname="CeraMediumTVATexte", fontfile=police_medium)
  x, y = left_pt_tvas, top_pt_tvas + taille_tva_seul
  for c in texte_tva_seul:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVATexte",
        fontsize=taille_tva_seul,
        color=(0, 0, 0),
    )
    x (
        += font_medium.text_length(c, fontsize=taille_tva_seul)
        + espacement_tva_seul
    )

  # 10. --- 20.0% ---
  texte_20 = "20.0%"
  taille_20 = 9.3
  espacement_20 = 0
  left_pt_20 = 30.8 / 25.4 * 72
  top_pt_20 = 77.8 / 25.4 * 72
  page.insert_font(fontname="CeraMedium20", fontfile=police_medium)
  x, y = left_pt_20, top_pt_20 + taille_20
  for c in texte_20:
    page.insert_text(
        (x, y), c, fontname="CeraMedium20", fontsize=taille_20, color=(0, 0, 0)
    )
    x += font_medium.text_length(c, fontsize=taille_20) + espacement_20

  # 10 bis. --- Montant TVA calculé ---
  taille_1e_nouveau = 9.5
  espacement_1e_nouveau = 0
  right_pt_1e_nouveau = 72.7 / 25.4 * 72
  top_pt_1e_nouveau = 77.6 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumMontantTVA2", fontfile=police_medium
  )
  largeur_totale_1e_nov = sum(
      font_medium.text_length(c, fontsize=taille_1e_nouveau)
      + espacement_1e_nouveau
      for c in tva_price
  )
  x, y = (
      right_pt_1e_nouveau - largeur_totale_1e_nov,
      top_pt_1e_nouveau + taille_1e_nouveau,
  )
  for c in tva_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantTVA2",
        fontsize=taille_1e_nouveau,
        color=(0, 0, 0),
    )
    x += (
        font_medium.text_length(c, fontsize=taille_1e_nouveau)
        + espacement_1e_nouveau
    )

  # 11. --- Total ---
  texte_tot_label = "Total"
  taille_tot_lab = 9.3
  espacement_tot_lab = 0
  left_pt_tl = 30.8 / 25.4 * 72
  top_pt_tl = 81.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumTotalLabel", fontfile=police_medium
  )
  x, y = left_pt_tl, top_pt_tl + taille_tot_lab
  for c in texte_tot_label:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalLabel",
        fontsize=taille_tot_lab,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_tot_lab) + espacement_tot_lab

  # 12. --- Premier texte (Prix article - Total) ---
  taille_1e = 9.5
  espacement_1e = -0.02
  right_pt_1e = 72.6 / 25.4 * 72
  top_pt_1e = 81.4 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumTotalMontant", fontfile=police_medium
  )
  largeur_totale_1e = sum(
      font_medium.text_length(c, fontsize=taille_1e) + espacement_1e
      for c in item_price
  )
  x, y = right_pt_1e - largeur_totale_1e, top_pt_1e + taille_1e
  for c in item_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalMontant",
        fontsize=taille_1e,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_1e) + espacement_1e

  # 13. --- Nombre d'articles : 1 ---
  texte_nb = "Nombre d'articles : 1"
  taille_nb = 9.5
  espacement_nb = 0
  left_pt_nb = 2.2 / 25.4 * 72
  top_pt_nb = 91 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumNbArticles", fontfile=police_medium
  )
  x, y = left_pt_nb, top_pt_nb + taille_nb
  for c in texte_nb:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumNbArticles",
        fontsize=taille_nb,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_nb) + espacement_nb

  # 13 bis. --- Total à payer ---
  texte_tap = "Total à payer"
  taille_tap = 11
  espacement_tap = -0.1
  left_pt_tap = 2.1 / 25.4 * 72
  top_pt_tap = 96.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraBoldTotalPayer", fontfile=police_bold
  )
  x, y = left_pt_tap, top_pt_tap + taille_tap
  for c in texte_tap:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTotalPayer",
        fontsize=taille_tap,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=taille_tap) + espacement_tap

  # 14. --- Prix Total à payer ---
  taille_tot_payer = 11
  espacement_tot_payer = 0
  right_pt_tp = 73 / 25.4 * 72
  top_pt_tp = 96.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraBoldPrixPayer", fontfile=police_bold
  )
  largeur_totale_tp = sum(
      font_bold.text_length(c, fontsize=taille_tot_payer)
      + espacement_tot_payer
      for c in item_price
  )
  x, y = right_pt_tp - largeur_totale_tp, top_pt_tp + taille_tot_payer
  for c in item_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldPrixPayer",
        fontsize=taille_tot_payer,
        color=(0, 0, 0),
    )
    x += (
        font_bold.text_length(c, fontsize=taille_tot_payer)
        + espacement_tot_payer
    )

  # 15. --- Payé avec Visa ---
  texte_paye = "Payé avec Visa"
  taille_paye = 9.5
  espacement_paye = 0
  left_pt_paye = 2.1 / 25.4 * 72
  top_pt_paye = 106.5 / 25.4 * 72
  page.insert_font(fontname="CeraMediumVisa", fontfile=police_medium)
  x, y = left_pt_paye, top_pt_paye + taille_paye
  for c in texte_paye:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumVisa",
        fontsize=taille_paye,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_paye) + espacement_paye

  # 16. --- Montant Visa aligné à droite ---
  taille_599e = 9.5
  espacement_599e = 0
  right_pt_599e = 72.8 / 25.4 * 72
  top_pt_599e = 106.5 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumMontantVisa", fontfile=police_medium
  )
  largeur_totale_599e = sum(
      font_medium.text_length(c, fontsize=taille_599e) + espacement_599e
      for c in item_price
  )
  x, y = right_pt_599e - largeur_totale_599e, top_pt_599e + taille_599e
  for c in item_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantVisa",
        fontsize=taille_599e,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_599e) + espacement_599e

  # 17. --- Image avis ---
  largeur_img_mm = 74
  left_img_pt = 0.6 / 25.4 * 72
  top_img_pt = 120.3 / 25.4 * 72
  largeur_img_pt = largeur_img_mm / 25.4 * 72
  img_doc = fitz.open(image_avis_path)
  hauteur_img_pt = (
      largeur_img_pt * (img_doc[0].rect.height / img_doc[0].rect.width)
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

  # 18. --- QR Code ---
  largeur_w99_mm = 14
  left_w99_pt = 23.7 / 25.4 * 72
  top_w99_pt = 124.5 / 25.4 * 72
  largeur_w99_pt = largeur_w99_mm / 25.4 * 72
  img_w99_doc = fitz.open(image_width99_path)
  hauteur_w99_pt = (
      largeur_w99_pt * (img_w99_doc[0].rect.height / img_w99_doc[0].rect.width)
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

  # 19. --- Textes d'avis fixe ---
  for texte, t_sz, esp, l_mm, t_mm, fname in [
      ("Comment jugez-", 10.5, 0, 39.8, 124.7, "CeraBoldJuger"),
      ("vous votre", 10.4, 0, 39.8, 129, "CeraBoldVousVotre"),
      ("expérience ?", 10.4, 0, 39.8, 133.2, "CeraBoldExperience"),
      (
          "Sinon, répondez en 3 minutes à notre",
          8,
          0,
          23.6,
          143.8,
          "CeraMediumSinon",
      ),
      (
          "questionnaire sur LEGO.com/",
          8,
          0,
          23.6,
          146.5,
          "CeraMediumQuestionnaire",
      ),
      ("storesurvey", 8, 0, 23.5, 149.3, "CeraMediumStoreSurvey"),
      ("Au besoin, utilisez ce code :", 8, 0, 23.5, 154.2, "CeraMediumAuBesoin"),
  ]:
    page.insert_font(fontname=fname, fontfile=police_bold if "Bold" in fname else police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + t_sz
    for c in texte:
      page.insert_text((x, y), c, fontname=fname, fontsize=t_sz, color=(0, 0, 0))
      x += (
          font_bold.text_length(c, fontsize=t_sz)
          if "Bold" in fname
          else font_medium.text_length(c, fontsize=t_sz)
      ) + esp

  # 25. --- Code d'avis (Dynamique) ---
  taille_code_besoin = 8
  espacement_code_besoin = 0.25
  left_pt_cb_code = 23.5 / 25.4 * 72
  top_pt_cb_code = 157 / 25.4 * 72
  page.insert_font(
      fontname="CeraMediumCodeBesoin", fontfile=police_medium
  )
  x, y = left_pt_cb_code, top_pt_cb_code + taille_code_besoin
  for c in code_besoin:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCodeBesoin",
        fontsize=taille_code_besoin,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_code_besoin) + espacement_code_besoin

  # 26. --- Lignes de séparation & Blocs suivants ---
  for y_m in [168, 196.2, 216.2, 293, 324.8, 345, 360.2]:
    shape = page.new_shape()
    shape.draw_line(
        fitz.Point(2.2 / 25.4 * 72, y_m / 25.4 * 72),
        fitz.Point(73 / 25.4 * 72, y_m / 25.4 * 72),
    )
    shape.finish(color=(0, 0, 0), width=1.3 if y_m in [216.2, 324.8, 360.2] else 1)
    shape.commit()

  # 27 à 37 : Blocs Insiders & S'abonner (textes fixes)
  insiders_texts = [
      ("Deviens un LEGO® Insider !", 10.5, 14, 170.8, "CeraBoldInsider", True),
      ("Rejoins le programme LEGO® Insiders pour", 9.7, 4, 177.2, "CeraMediumInsider1", False),
      ("profiter de formidables avantages et", 9.7, 8.8, 180.7, "CeraMediumInsider2", False),
      ("récompenses LEGO®", 9.7, 21.3, 184, "CeraMediumInsider3", False),
      ("LEGO.com/insiders", 9.7, 22.2, 189, "CeraMediumInsiderUrl", False),
      ("S'abonner aux e-mails", 10.5, 18.3, 198.8, "CeraBoldAbonner", True),
      ("Suivez notre actualité en vous abonnant à", 9.5, 4.8, 205.5, "CeraMediumAbonner1", False),
      ("notre programme d'e-mails LEGO.com/email", 9.5, 2.5, 208.8, "CeraMediumAbonner2", False),
      ("Caractéristiques de sécurité", 10.5, 12.9, 218.8, "CeraBoldSecurite", True),
  ]
  for txt, sz, l_mm, t_mm, fname, is_b in insiders_texts:
    page.insert_font(fontname=fname, fontfile=police_bold if is_b else police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # 38. --- Image width200.png ---
  largeur_w200_mm = 38.1
  left_w200_pt = 18.4 / 25.4 * 72
  top_w200_pt = 228.8 / 25.4 * 72
  largeur_w200_pt = largeur_w200_mm / 25.4 * 72
  img_w200_doc = fitz.open(image_width200_path)
  hauteur_w200_pt = largeur_w200_pt * (img_w200_doc[0].rect.height / img_w200_doc[0].rect.width)
  page.insert_image(
      fitz.Rect(left_w200_pt, top_w200_pt, left_w200_pt + largeur_w200_pt, top_w200_pt + hauteur_w200_pt),
      filename=image_width200_path,
  )

  # 40 à 45 : Mentions légales bas de page
  legals = [
      ("Duplicata", 7.2, 2, 268.1, "CeraBoldDuplicata", True),
      ("1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286", 7.2, 2, 270.8, "CeraMediumDuplicataRef", False),
      ("Système de caisse certifié LNE", 7.2, 2, 273.1, "CeraMediumLNE", False),
      ("LEGO BRAND RETAIL S.A.S est enregistré au Registre", 7.2, 6.5, 278.5, "CeraMediumLegal1", False),
      ("national des metteurs sur le marché des jeux et jouets sous", 7.2, 2.5, 281, "CeraMediumLegal2", False),
      ("le numéro FR214763_12TBLL.", 7.2, 20.8, 283.5, "CeraMediumLegal3", False),
  ]
  for txt, sz, l_mm, t_mm, fname, is_b in legals:
    page.insert_font(fontname=fname, fontfile=police_bold if is_b else police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # 46 à 58 : Ticket de carte bancaire & Valeurs dynamiques (Date et heure CB)
  cb_blocks = [
      ("Ticket de carte bancaire", 10.5, 2, 295.2, "CeraBoldCBTitre", True),
      ("Date/Heure", 9.5, 2, 300.8, "CeraMediumCBDate", False),
      (date_time, 9.5, 40.8, 300.8, "CeraMediumCBValeurDate", False),
      ("Carte", 9.5, 2, 304, "CeraMediumCBCarte", False),
      ("**** 0777", 9.5, 59, 304, "CeraMediumCBNumero", False),
      ("Type de carte", 9.5, 2, 307.2, "CeraMediumCBTypeCarte", False),
      ("Visa", 9.5, 66.6, 307.2, "CeraMediumCBVisa", False),
      ("Type de saisie", 9.5, 2, 310.8, "CeraMediumCBTypeSaisie", False),
      ("Puce sans contact", 9.5, 44.7, 310.8, "CeraMediumCBPuce", False),
      ("AID", 9.5, 2, 314.2, "CeraMediumCBAID", False),
      ("A0000000031010", 9.5, 45.5, 314.2, "CeraMediumCBAIDValeur", False),
      ("Code d'autor.", 9.5, 2, 317.3, "CeraMediumCBAutor", False),
      ("056013", 9.5, 62, 317.3, "CeraMediumCBAutorValeur", False),
  ]
  for txt, sz, l_mm, t_mm, fname, is_b in cb_blocks:
    page.insert_font(fontname=fname, fontfile=police_bold if is_b else police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # 60. --- Image width87.png ---
  largeur_w87_mm = 13.8
  left_w87_pt = 59 / 25.4 * 72
  top_w87_pt = 328 / 25.4 * 72
  largeur_w87_pt = largeur_w87_mm / 25.4 * 72
  img_w87_doc = fitz.open(image_width87_path)
  hauteur_w87_pt = largeur_w87_pt * (img_w87_doc[0].rect.height / img_w87_doc[0].rect.width)
  page.insert_image(
      fitz.Rect(left_w87_pt, top_w87_pt, left_w87_pt + largeur_w87_pt, top_w87_pt + hauteur_w87_pt),
      filename=image_width87_path,
  )

  # 61 à 66 : Détails de la commande (Date et heure dynamiques)
  details_blocks = [
      ("Détails de la commande", 10.5, 2, 327.3, "CeraBoldDetailsCommande", True),
      ("Transaction n°:", 8, 2, 332.8, "CeraMediumDetailsTransaction", False),
      ("LEGO0064863689", 8, 30.5, 332.8, "CeraMediumDetailsTransactionValeur", False),
      ("Date et heure:", 8, 2, 335.3, "CeraMediumDetailsDateLabel", False),
      (date_long, 8, 30.5, 335.3, "CeraMediumDetailsDateValeur", False),
      (heure, 8, 30.4, 338.2, "CeraMediumDetailsHeureValeur", False),
  ]
  for txt, sz, l_mm, t_mm, fname, is_b in details_blocks:
    page.insert_font(fontname=fname, fontfile=police_bold if is_b else police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # 68 à 75 : Garanties et adresses finales fixes
  foot_blocks = [
      ("Ce bien bénéficie auprès du vendeur d’une garantie", 8, 3.3, 347.8, "CeraMediumGarantieL1"),
      ("légale de conformité d’une durée de deux ans à", 8, 6, 350.8, "CeraMediumGarantieL2"),
      ("compter de sa remise au consommateur.", 8, 10.7, 353.5, "CeraMediumGarantieL3"),
      ("LEGO Brand Retail SAS", 8, 22.5, 365.8, "CeraMediumRetailL1"),
      ("75 rue de Tocqueville,", 8, 23.2, 368.8, "CeraMediumRetailL2"),
      ("75017 Paris, FR", 8, 28, 371.5, "CeraMediumRetailL3"),
      ("FR 61752526178", 8, 27.4, 374.2, "CeraMediumRetailL4"),
  ]
  for txt, sz, l_mm, t_mm, fname in foot_blocks:
    page.insert_font(fontname=fname, fontfile=police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += font_medium.text_length(c, fontsize=sz)

  # Sauvegarde finale
  meta = doc.metadata
  meta["title"] = "Receipt"
  doc.set_metadata(meta)
  doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
  doc.close()