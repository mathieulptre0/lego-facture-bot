import os
import pymupdf as fitz


def executer_generation_complete():
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

  print(f"PDF créé : {pdf_path}")
  print(f"Taille : {width_mm} x {height_mm} mm")

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

  x = left_pt_dh
  y = top_pt_dh + taille_dh

  for c in texte_duplicata_haut:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldHaut",
        fontsize=taille_dh,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_dh)
    x += largeur_c + espacement_dh

  print("Texte 'DUPLICATA' (haut) inséré dans le PDF.")

  # 3. --- Insertion de l'image (width60.png) ---
  largeur_w60_mm = 19
  left_w60_mm = 28
  top_w60_mm = 15.3

  left_w60_pt = left_w60_mm / 25.4 * 72
  top_w60_pt = top_w60_mm / 25.4 * 72
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

  print("Image 'width60.png' insérée dans le PDF.")

  # 4. --- Insertion du texte "149 LEGO, LQT Paris, EU-FR" ---
  texte_lqt = "149 LEGO, LQT Paris, EU-FR"
  taille_lqt = 7.9
  espacement_lqt = 0.03

  left_mm_lqt = 20
  top_mm_lqt = 40.4
  left_pt_lqt = left_mm_lqt / 25.4 * 72
  top_pt_lqt = top_mm_lqt / 25.4 * 72

  page.insert_font(fontname="CeraMediumLQT", fontfile=police_medium)

  x = left_pt_lqt
  y = top_pt_lqt + taille_lqt

  for c in texte_lqt:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLQT",
        fontsize=taille_lqt,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_lqt)
    x += largeur_c + espacement_lqt

  print("Texte '149 LEGO, LQT Paris, EU-FR' inséré dans le PDF.")

  # 5. --- Insertion de la deuxième ligne d'adresse ---
  texte_adr2 = "15 Parv. de la Défense,"
  taille_adr2 = 7.9
  espacement_adr2 = 0

  left_mm_adr2 = 23
  top_mm_adr2 = 43.2
  left_pt_adr2 = left_mm_adr2 / 25.4 * 72
  top_pt_adr2 = top_mm_adr2 / 25.4 * 72

  page.insert_font(fontname="CeraMedium2", fontfile=police_medium)

  x = left_pt_adr2
  y = top_pt_adr2 + taille_adr2

  for c in texte_adr2:
    page.insert_text(
        (x, y), c, fontname="CeraMedium2", fontsize=taille_adr2, color=(0, 0, 0)
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_adr2)
    x += largeur_c + espacement_adr2

  print("Deuxième ligne d'adresse insérée dans le PDF.")

  # 6. --- Insertion de la troisième ligne d'adresse ---
  texte_adr3 = "92092 Puteaux, FR"
  taille_adr3 = 7.9
  espacement_adr3 = 0

  left_mm_adr3 = 25.5
  top_mm_adr3 = 46.2
  left_pt_adr3 = left_mm_adr3 / 25.4 * 72
  top_pt_adr3 = top_mm_adr3 / 25.4 * 72

  page.insert_font(fontname="CeraMedium3", fontfile=police_medium)

  x = left_pt_adr3
  y = top_pt_adr3 + taille_adr3

  for c in texte_adr3:
    page.insert_text(
        (x, y), c, fontname="CeraMedium3", fontsize=taille_adr3, color=(0, 0, 0)
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_adr3)
    x += largeur_c + espacement_adr3

  print("Troisième ligne d'adresse insérée dans le PDF.")

  # 6 bis. --- Insertion du texte "Transaction de vente" ---
  texte_trans = "Transaction de vente"
  taille_trans = 15
  espacement_trans = 0

  left_mm_tr = 11
  top_mm_tr = 54.5
  left_pt_tr = left_mm_tr / 25.4 * 72
  top_pt_tr = top_mm_tr / 25.4 * 72

  page.insert_font(fontname="CeraBoldTrans", fontfile=police_bold)

  x = left_pt_tr
  y = top_pt_tr + taille_trans

  for c in texte_trans:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTrans",
        fontsize=taille_trans,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_trans)
    x += largeur_c + espacement_trans

  print("Texte 'Transaction de vente' inséré dans le PDF.")

  # 7. --- Insertion de l'article "Porte-clés Miles Morales" ---
  texte_article = "Porte-clés Miles Morales"
  taille_article = 9.5
  espacement_article = 0

  left_mm_art = 2
  top_mm_art = 66
  left_pt_art = left_mm_art / 25.4 * 72
  top_pt_art = top_mm_art / 25.4 * 72

  page.insert_font(fontname="CeraMediumArt1", fontfile=police_medium)

  x = left_pt_art
  y = top_pt_art + taille_article

  for c in texte_article:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumArt1",
        fontsize=taille_article,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_article)
    x += largeur_c + espacement_article

  print("Article 'Porte-clés Miles Morales' inséré dans le PDF.")

  # 8. --- Insertion du prix de l'article "5,99 €" (aligné à droite) ---
  texte_p1 = "5,99 €"
  taille_p1 = 9.5
  espacement_p1 = 0

  right_mm_p1 = 72.5
  top_mm_p1 = 66
  right_pt_p1 = right_mm_p1 / 25.4 * 72
  top_pt_p1 = top_mm_p1 / 25.4 * 72

  page.insert_font(fontname="CeraMediumPrix1", fontfile=police_medium)

  largeur_totale_p1 = sum(
      font_medium.text_length(c, fontsize=taille_p1) + espacement_p1
      for c in texte_p1
  )
  x = right_pt_p1 - largeur_totale_p1
  y = top_pt_p1 + taille_p1

  for c in texte_p1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumPrix1",
        fontsize=taille_p1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_p1)
    x += largeur_c + espacement_p1

  print("Prix '5,99 €' (aligné à droite) inséré dans le PDF.")

  # 9. --- Insertion du texte "Récapitulatif TVA Taux" ---
  texte_tva_taux = "Récapitulatif TVA  Taux"
  taille_tva_taux = 9.3
  espacement_tva_taux = 0

  left_mm_tva = 2.2
  top_mm_tva = 73.6
  left_pt_tva = left_mm_tva / 25.4 * 72
  top_pt_tva = top_mm_tva / 25.4 * 72

  page.insert_font(fontname="CeraMediumTVA", fontfile=police_medium)

  x = left_pt_tva
  y = top_pt_tva + taille_tva_taux

  for c in texte_tva_taux:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVA",
        fontsize=taille_tva_taux,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_tva_taux)
    x += largeur_c + espacement_tva_taux

  print("Texte 'Récapitulatif TVA Taux' inséré dans le PDF.")

  # 9 bis. --- Insertion du texte "TVA" ---
  texte_tva_seul = "TVA"
  taille_tva_seul = 9.2
  espacement_tva_seul = 0

  left_mm_tvas = 66.5
  top_mm_tvas = 73.7
  left_pt_tvas = left_mm_tvas / 25.4 * 72
  top_pt_tvas = top_mm_tvas / 25.4 * 72

  page.insert_font(fontname="CeraMediumTVATexte", fontfile=police_medium)

  x = left_pt_tvas
  y = top_pt_tvas + taille_tva_seul

  for c in texte_tva_seul:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTVATexte",
        fontsize=taille_tva_seul,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_tva_seul)
    x += largeur_c + espacement_tva_seul

  print("Texte 'TVA' inséré dans le PDF.")

  # 10. --- Insertion du texte "20.0%" ---
  texte_20 = "20.0%"
  taille_20 = 9.3
  espacement_20 = 0

  left_mm_20 = 30.8
  top_mm_20 = 77.8
  left_pt_20 = left_mm_20 / 25.4 * 72
  top_pt_20 = top_mm_20 / 25.4 * 72

  page.insert_font(fontname="CeraMedium20", fontfile=police_medium)

  x = left_pt_20
  y = top_pt_20 + taille_20

  for c in texte_20:
    page.insert_text(
        (x, y), c, fontname="CeraMedium20", fontsize=taille_20, color=(0, 0, 0)
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_20)
    x += largeur_c + espacement_20

  print("Texte '20.0%' inséré dans le PDF.")

  # 10 bis. --- Insertion du NOUVEAU montant "1,00 €" ---
  texte_1e_nouveau = "1,00 €"
  taille_1e_nouveau = 9.5
  espacement_1e_nouveau = 0

  right_mm_1e_nouveau = 72.7
  top_mm_1e_nouveau = 77.6
  right_pt_1e_nouveau = right_mm_1e_nouveau / 25.4 * 72
  top_pt_1e_nouveau = top_mm_1e_nouveau / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumMontantTVA2", fontfile=police_medium
  )

  largeur_totale_1e_nov = sum(
      font_medium.text_length(c, fontsize=taille_1e_nouveau)
      + espacement_1e_nouveau
      for c in texte_1e_nouveau
  )
  x = right_pt_1e_nouveau - largeur_totale_1e_nov
  y = top_pt_1e_nouveau + taille_1e_nouveau

  for c in texte_1e_nouveau:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantTVA2",
        fontsize=taille_1e_nouveau,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_1e_nouveau)
    x += largeur_c + espacement_1e_nouveau

  print("Second texte '1,00 €' inséré dans le PDF (emplacement TVA).")

  # 11. --- Insertion du texte "Total" ---
  texte_tot_label = "Total"
  taille_tot_lab = 9.3
  espacement_tot_lab = 0

  left_mm_tl = 30.8
  top_mm_tl = 81.5
  left_pt_tl = left_mm_tl / 25.4 * 72
  top_pt_tl = top_mm_tl / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumTotalLabel", fontfile=police_medium
  )

  x = left_pt_tl
  y = top_pt_tl + taille_tot_lab

  for c in texte_tot_label:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalLabel",
        fontsize=taille_tot_lab,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_tot_lab)
    x += largeur_c + espacement_tot_lab

  print("Texte 'Total' inséré dans le PDF.")

  # 12. --- Insertion du premier texte "1,00 €" ---
  texte_1e = "1,00 €"
  taille_1e = 9.5
  espacement_1e = -0.02

  right_mm_1e = 72.6
  top_mm_1e = 81.4
  right_pt_1e = right_mm_1e / 25.4 * 72
  top_pt_1e = top_mm_1e / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumTotalMontant", fontfile=police_medium
  )

  largeur_totale_1e = sum(
      font_medium.text_length(c, fontsize=taille_1e) + espacement_1e
      for c in texte_1e
  )
  x = right_pt_1e - largeur_totale_1e
  y = top_pt_1e + taille_1e

  for c in texte_1e:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumTotalMontant",
        fontsize=taille_1e,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_1e)
    x += largeur_c + espacement_1e

  print("Texte '1,00 €' (aligné à droite - Total) inséré dans le PDF.")

  # 13. --- Insertion du texte "Nombre d'articles : 1" ---
  texte_nb = "Nombre d'articles : 1"
  taille_nb = 9.5
  espacement_nb = 0

  left_mm_nb = 2.2
  top_mm_nb = 91
  left_pt_nb = left_mm_nb / 25.4 * 72
  top_pt_nb = top_mm_nb / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumNbArticles", fontfile=police_medium
  )

  x = left_pt_nb
  y = top_pt_nb + taille_nb

  for c in texte_nb:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumNbArticles",
        fontsize=taille_nb,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_nb)
    x += largeur_c + espacement_nb

  print("Texte 'Nombre d'articles : 1' inséré dans le PDF.")

  # 13 bis. --- Insertion du texte "Total à payer" ---
  texte_tap = "Total à payer"
  taille_tap = 11
  espacement_tap = -0.1

  left_mm_tap = 2.1
  top_mm_tap = 96.5
  left_pt_tap = left_mm_tap / 25.4 * 72
  top_pt_tap = top_mm_tap / 25.4 * 72

  page.insert_font(
      fontname="CeraBoldTotalPayer", fontfile=police_bold
  )

  x = left_pt_tap
  y = top_pt_tap + taille_tap

  for c in texte_tap:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTotalPayer",
        fontsize=taille_tap,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_tap)
    x += largeur_c + espacement_tap

  print("Texte 'Total à payer' inséré dans le PDF.")

  # 14. --- Insertion du texte "5,99 €" (Total à payer) ---
  texte_tot_payer = "5,99 €"
  taille_tot_payer = 11
  espacement_tot_payer = 0

  right_mm_tp = 73
  top_mm_tp = 96.5
  right_pt_tp = right_mm_tp / 25.4 * 72
  top_pt_tp = top_mm_tp / 25.4 * 72

  page.insert_font(
      fontname="CeraBoldPrixPayer", fontfile=police_bold
  )

  largeur_totale_tp = sum(
      font_bold.text_length(c, fontsize=taille_tot_payer)
      + espacement_tot_payer
      for c in texte_tot_payer
  )
  x = right_pt_tp - largeur_totale_tp
  y = top_pt_tp + taille_tot_payer

  for c in texte_tot_payer:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldPrixPayer",
        fontsize=taille_tot_payer,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_tot_payer)
    x += largeur_c + espacement_tot_payer

  print("Texte '5,99 €' (aligné à droite - Total à payer) inséré dans le PDF.")

  # 15. --- Insertion du texte "Payé avec Visa" ---
  texte_paye = "Payé avec Visa"
  taille_paye = 9.5
  espacement_paye = 0

  left_mm_paye = 2.1
  top_mm_paye = 106.5
  left_pt_paye = left_mm_paye / 25.4 * 72
  top_pt_paye = top_mm_paye / 25.4 * 72

  page.insert_font(fontname="CeraMediumVisa", fontfile=police_medium)

  x = left_pt_paye
  y = top_pt_paye + taille_paye

  for c in texte_paye:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumVisa",
        fontsize=taille_paye,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_paye)
    x += largeur_c + espacement_paye

  print("Texte 'Payé avec Visa' inséré dans le PDF.")

  # 16. --- Insertion du montant Visa aligné à droite ---
  texte_599e = "5,99 €"
  taille_599e = 9.5
  espacement_599e = 0

  right_mm_599e = 72.8
  top_mm_599e = 106.5
  right_pt_599e = right_mm_599e / 25.4 * 72
  top_pt_599e = top_mm_599e / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumMontantVisa", fontfile=police_medium
  )

  largeur_totale_599e = sum(
      font_medium.text_length(c, fontsize=taille_599e) + espacement_599e
      for c in texte_599e
  )
  x = right_pt_599e - largeur_totale_599e
  y = top_pt_599e + taille_599e

  for c in texte_599e:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumMontantVisa",
        fontsize=taille_599e,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_599e)
    x += largeur_c + espacement_599e

  print("Texte '5,99 €' (aligné à droite) inséré dans le PDF.")

  # 17. --- Insertion de l'image (avis / code) ---
  largeur_img_mm = 74
  left_img_mm = 0.6
  top_img_mm = 120.3

  left_img_pt = left_img_mm / 25.4 * 72
  top_img_pt = top_img_mm / 25.4 * 72
  largeur_img_pt = largeur_img_mm / 25.4 * 72

  img_doc = fitz.open(image_avis_path)
  ratio = img_doc[0].rect.height / img_doc[0].rect.width
  hauteur_img_pt = largeur_img_pt * ratio

  rect_img = fitz.Rect(
      left_img_pt,
      top_img_pt,
      left_img_pt + largeur_img_pt,
      top_img_pt + hauteur_img_pt,
  )
  page.insert_image(rect_img, filename=image_avis_path)

  print("Image avis insérée avec succès dans le PDF.")

  # 18. --- Insertion de l'image "width99.png" (QR Code) ---
  largeur_w99_mm = 14
  left_w99_mm = 23.7
  top_w99_mm = 124.5

  left_w99_pt = left_w99_mm / 25.4 * 72
  top_w99_pt = top_w99_mm / 25.4 * 72
  largeur_w99_pt = largeur_w99_mm / 25.4 * 72

  img_w99_doc = fitz.open(image_width99_path)
  ratio_w99 = img_w99_doc[0].rect.height / img_w99_doc[0].rect.width
  hauteur_w99_pt = largeur_w99_pt * ratio_w99

  rect_w99 = fitz.Rect(
      left_w99_pt,
      top_w99_pt,
      left_w99_pt + largeur_w99_pt,
      top_w99_pt + hauteur_w99_pt,
  )
  page.insert_image(rect_w99, filename=image_width99_path)

  print("QR Code (width99.png) inséré dans le PDF.")

  # 19. --- Insertion du texte "Comment jugez-" ---
  texte_juger = "Comment jugez-"
  taille_juger = 10.5
  espacement_juger = 0

  left_mm_juger = 39.8
  top_mm_juger = 124.7
  left_pt_juger = left_mm_juger / 25.4 * 72
  top_pt_juger = top_mm_juger / 25.4 * 72

  page.insert_font(fontname="CeraBoldJuger", fontfile=police_bold)

  x = left_pt_juger
  y = top_pt_juger + taille_juger

  for c in texte_juger:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldJuger",
        fontsize=taille_juger,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_juger)
    x += largeur_c + espacement_juger

  print("Texte 'Comment jugez-' inséré dans le PDF.")

  # 19 bis. --- Insertion du texte "vous votre" ---
  texte_vv = "vous votre"
  taille_vv = 10.4
  espacement_vv = 0

  left_mm_vv = 39.8
  top_mm_vv = 129
  left_pt_vv = left_mm_vv / 25.4 * 72
  top_pt_vv = top_mm_vv / 25.4 * 72

  page.insert_font(
      fontname="CeraBoldVousVotre", fontfile=police_bold
  )

  x = left_pt_vv
  y = top_pt_vv + taille_vv

  for c in texte_vv:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldVousVotre",
        fontsize=taille_vv,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_vv)
    x += largeur_c + espacement_vv

  print("Texte 'vous votre' inséré dans le PDF.")

  # 20. --- Insertion du texte "expérience ?" ---
  texte_exp = "expérience ?"
  taille_exp = 10.4
  espacement_exp = 0

  left_mm_exp = 39.8
  top_mm_exp = 133.2
  left_pt_exp = left_mm_exp / 25.4 * 72
  top_pt_exp = top_mm_exp / 25.4 * 72

  page.insert_font(
      fontname="CeraBoldExperience", fontfile=police_bold
  )

  x = left_pt_exp
  y = top_pt_exp + taille_exp

  for c in texte_exp:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldExperience",
        fontsize=taille_exp,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_exp)
    x += largeur_c + espacement_exp

  print("Texte 'expérience ?' inséré dans le PDF.")

  # 21. --- Insertion du texte "Sinon, répondez en 3 minutes à notre" ---
  texte_sinon = "Sinon, répondez en 3 minutes à notre"
  taille_sinon = 8
  espacement_sinon = 0

  left_mm_sinon = 23.6
  top_mm_sinon = 143.8
  left_pt_sinon = left_mm_sinon / 25.4 * 72
  top_pt_sinon = top_mm_sinon / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumSinon", fontfile=police_medium
  )

  x = left_pt_sinon
  y = top_pt_sinon + taille_sinon

  for c in texte_sinon:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumSinon",
        fontsize=taille_sinon,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_sinon)
    x += largeur_c + espacement_sinon

  print("Texte 'Sinon, répondez en 3 minutes à notre' inséré dans le PDF.")

  # 22. --- Insertion du texte "questionnaire sur LEGO.com/" ---
  texte_quest = "questionnaire sur LEGO.com/"
  taille_quest = 8
  espacement_quest = 0

  left_mm_quest = 23.6
  top_mm_quest = 146.5
  left_pt_quest = left_mm_quest / 25.4 * 72
  top_pt_quest = top_mm_quest / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumQuestionnaire", fontfile=police_medium
  )

  x = left_pt_quest
  y = top_pt_quest + taille_quest

  for c in texte_quest:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumQuestionnaire",
        fontsize=taille_quest,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_quest)
    x += largeur_c + espacement_quest

  print("Texte 'questionnaire sur LEGO.com/' inséré dans le PDF.")

  # 23. --- Insertion du texte "storesurvey" ---
  texte_ss = "storesurvey"
  taille_ss = 8
  espacement_ss = 0

  left_mm_ss = 23.5
  top_mm_ss = 149.3
  left_pt_ss = left_mm_ss / 25.4 * 72
  top_pt_ss = top_mm_ss / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumStoreSurvey", fontfile=police_medium
  )

  x = left_pt_ss
  y = top_pt_ss + taille_ss

  for c in texte_ss:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumStoreSurvey",
        fontsize=taille_ss,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ss)
    x += largeur_c + espacement_ss

  print("Texte 'storesurvey' inséré dans le PDF.")

  # 24. --- Insertion du texte "Au besoin, utilisez ce code :" ---
  texte_besoin = "Au besoin, utilisez ce code :"
  taille_besoin = 8
  espacement_besoin = 0

  left_mm_besoin = 23.5
  top_mm_besoin = 154.2
  left_pt_besoin = left_mm_besoin / 25.4 * 72
  top_pt_besoin = top_mm_besoin / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumAuBesoin", fontfile=police_medium
  )

  x = left_pt_besoin
  y = top_pt_besoin + taille_besoin

  for c in texte_besoin:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAuBesoin",
        fontsize=taille_besoin,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_besoin)
    x += largeur_c + espacement_besoin

  print("Texte 'Au besoin, utilisez ce code :' inséré dans le PDF.")

  # 25. --- Insertion du code d'avis ---
  texte_code_besoin = "149-64863689-08-24-2026 "
  taille_code_besoin = 8
  espacement_code_besoin = 0.25

  left_mm_cb_code = 23.5
  top_mm_cb_code = 157
  left_pt_cb_code = left_mm_cb_code / 25.4 * 72
  top_pt_cb_code = top_mm_cb_code / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCodeBesoin", fontfile=police_medium
  )

  x = left_pt_cb_code
  y = top_pt_cb_code + taille_code_besoin

  for c in texte_code_besoin:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCodeBesoin",
        fontsize=taille_code_besoin,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_code_besoin)
    x += largeur_c + espacement_code_besoin

  print("Texte '149-64863689-08-24-2026 ' inséré dans le PDF.")

  # 26. --- Insertion de la ligne de séparation vectorielle (top_mm = 168) ---
  shape_s1 = page.new_shape()
  shape_s1.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 168 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 168 / 25.4 * 72),
  )
  shape_s1.finish(color=(0, 0, 0), width=1)
  shape_s1.commit()

  print("Ligne de séparation vectorielle insérée dans le PDF.")

  # 27. --- Insertion du texte "Deviens un LEGO® Insider !" ---
  texte_ins_titre = "Deviens un LEGO® Insider !"
  taille_ins_titre = 10.5
  espacement_ins_titre = 0

  left_mm_it = 14
  top_mm_it = 170.8
  left_pt_it = left_mm_it / 25.4 * 72
  top_pt_it = top_mm_it / 25.4 * 72

  page.insert_font(fontname="CeraBoldInsider", fontfile=police_bold)

  x = left_pt_it
  y = top_pt_it + taille_ins_titre

  for c in texte_ins_titre:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldInsider",
        fontsize=taille_ins_titre,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_ins_titre)
    x += largeur_c + espacement_ins_titre

  print("Texte 'Deviens un LEGO® Insider !' inséré dans le PDF.")

  # 28. --- Insertion du texte d'insiders (Ligne 1) ---
  texte_ins1 = "Rejoins le programme LEGO® Insiders pour"
  taille_ins1 = 9.7
  espacement_ins1 = -0.1

  left_mm_in1 = 4
  top_mm_in1 = 177.2
  left_pt_in1 = left_mm_in1 / 25.4 * 72
  top_pt_in1 = top_mm_in1 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumInsider1", fontfile=police_medium
  )

  x = left_pt_in1
  y = top_pt_in1 + taille_ins1

  for c in texte_ins1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider1",
        fontsize=taille_ins1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ins1)
    x += largeur_c + espacement_ins1

  print("Texte 'Rejoins le programme LEGO® Insiders pour' inséré dans le PDF.")

  # 29. --- Insertion du texte d'insiders (Ligne 2) ---
  texte_ins2 = "profiter de formidables avantages et"
  taille_ins2 = 9.7
  espacement_ins2 = -0.1

  left_mm_in2 = 8.8
  top_mm_in2 = 180.7
  left_pt_in2 = left_mm_in2 / 25.4 * 72
  top_pt_in2 = top_mm_in2 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumInsider2", fontfile=police_medium
  )

  x = left_pt_in2
  y = top_pt_in2 + taille_ins2

  for c in texte_ins2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider2",
        fontsize=taille_ins2,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ins2)
    x += largeur_c + espacement_ins2

  print("Texte 'profiter de formidables avantages et' inséré dans le PDF.")

  # 30. --- Insertion du texte d'insiders (Ligne 3) ---
  texte_ins3 = "récompenses LEGO®"
  taille_ins3 = 9.7
  espacement_ins3 = -0.1

  left_mm_in3 = 21.3
  top_mm_in3 = 184
  left_pt_in3 = left_mm_in3 / 25.4 * 72
  top_pt_in3 = top_mm_in3 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumInsider3", fontfile=police_medium
  )

  x = left_pt_in3
  y = top_pt_in3 + taille_ins3

  for c in texte_ins3:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsider3",
        fontsize=taille_ins3,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ins3)
    x += largeur_c + espacement_ins3

  print("Texte 'récompenses LEGO®' inséré dans le PDF.")

  # 31. --- Insertion du texte "LEGO.com/insiders" ---
  texte_ins_url = "LEGO.com/insiders"
  taille_ins_url = 9.7
  espacement_ins_url = -0.24

  left_mm_iu = 22.2
  top_mm_iu = 189
  left_pt_iu = left_mm_iu / 25.4 * 72
  top_pt_iu = top_mm_iu / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumInsiderUrl", fontfile=police_medium
  )

  x = left_pt_iu
  y = top_pt_iu + taille_ins_url

  for c in texte_ins_url:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumInsiderUrl",
        fontsize=taille_ins_url,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ins_url)
    x += largeur_c + espacement_ins_url

  print("Texte 'LEGO.com/insiders' inséré dans le PDF.")

  # 32. --- Insertion de la ligne de séparation vectorielle (top_mm = 196.2) ---
  shape_s2 = page.new_shape()
  shape_s2.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 196.2 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 196.2 / 25.4 * 72),
  )
  shape_s2.finish(color=(0, 0, 0), width=1)
  shape_s2.commit()

  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 33. --- Insertion du titre "S'abonner aux e-mails" ---
  texte_titre = "S'abonner aux e-mails"
  taille_police_titre = 10.5
  espacement_lettres_titre = 0

  left_mm_titre = 18.3
  top_mm_titre = 198.8
  left_pt_titre = left_mm_titre / 25.4 * 72
  top_pt_titre = top_mm_titre / 25.4 * 72

  page.insert_font(fontname="CeraBoldAbonner", fontfile=police_bold)

  x = left_pt_titre
  y = top_pt_titre + taille_police_titre

  for c in texte_titre:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldAbonner",
        fontsize=taille_police_titre,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_police_titre)
    x += largeur_c + espacement_lettres_titre

  print("Texte 'S\\'abonner aux e-mails' inséré dans le PDF.")

  # 34. --- Insertion du texte d'abonnement (ligne 1) ---
  texte_l1 = "Suivez notre actualité en vous abonnant à"
  taille_police_l1 = 9.5
  espacement_lettres_l1 = -0.02

  left_mm_l1 = 4.8
  top_mm_l1 = 205.5
  left_pt_l1 = left_mm_l1 / 25.4 * 72
  top_pt_l1 = top_mm_l1 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumAbonner1", fontfile=police_medium
  )

  x = left_pt_l1
  y = top_pt_l1 + taille_police_l1

  for c in texte_l1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAbonner1",
        fontsize=taille_police_l1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_police_l1)
    x += largeur_c + espacement_lettres_l1

  print("Texte 'Suivez notre actualité en vous abonnant à' inséré dans le PDF.")

  # 35. --- Insertion du texte d'abonnement (ligne 2) ---
  texte_l2 = "notre programme d'e-mails LEGO.com/email"
  taille_police_l2 = 9.5
  espacement_lettres_l2 = -0.05

  left_mm_l2 = 2.5
  top_mm_l2 = 208.8
  left_pt_l2 = left_mm_l2 / 25.4 * 72
  top_pt_l2 = top_mm_l2 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumAbonner2", fontfile=police_medium
  )

  x = left_pt_l2
  y = top_pt_l2 + taille_police_l2

  for c in texte_l2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumAbonner2",
        fontsize=taille_police_l2,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_police_l2)
    x += largeur_c + espacement_lettres_l2

  print("Texte 'notre programme d\\'e-mails LEGO.com/email' inséré dans le PDF.")

  # 36. --- Insertion de la ligne de séparation vectorielle (top_mm = 216.2) ---
  shape_s3 = page.new_shape()
  shape_s3.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 216.2 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 216.2 / 25.4 * 72),
  )
  shape_s3.finish(color=(0, 0, 0), width=1.3)
  shape_s3.commit()

  print("Dernière ligne de séparation vectorielle insérée dans le PDF.")

  # 37. --- Insertion du titre "Caractéristiques de sécurité" ---
  texte_secu = "Caractéristiques de sécurité"
  taille_secu = 10.5
  espacement_secu = 0

  left_mm_sec = 12.9
  top_mm_sec = 218.8
  left_pt_sec = left_mm_sec / 25.4 * 72
  top_pt_sec = top_mm_sec / 25.4 * 72

  page.insert_font(fontname="CeraBoldSecurite", fontfile=police_bold)

  x = left_pt_sec
  y = top_pt_sec + taille_secu

  for c in texte_secu:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldSecurite",
        fontsize=taille_secu,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_secu)
    x += largeur_c + espacement_secu

  print("Texte 'Caractéristiques de sécurité' inséré dans le PDF.")

  # 38. --- Insertion de l'image "width200.png" ---
  largeur_w200_mm = 38.1
  left_w200_mm = 18.4
  top_w200_mm = 228.8

  left_w200_pt = left_w200_mm / 25.4 * 72
  top_w200_pt = top_w200_mm / 25.4 * 72
  largeur_w200_pt = largeur_w200_mm / 25.4 * 72

  img_w200_doc = fitz.open(image_width200_path)
  ratio_w200 = img_w200_doc[0].rect.height / img_w200_doc[0].rect.width
  hauteur_w200_pt = largeur_w200_pt * ratio_w200

  rect_w200 = fitz.Rect(
      left_w200_pt,
      top_w200_pt,
      left_w200_pt + largeur_w200_pt,
      top_w200_pt + hauteur_w200_pt,
  )
  page.insert_image(rect_w200, filename=image_width200_path)

  print("Image 'width200.png' insérée dans le PDF.")

  # 39. --- Insertion de la ligne de séparation vectorielle (top_mm = 293) ---
  shape_s4 = page.new_shape()
  shape_s4.draw_line(
      fitz.Point(2.2 / 25.4 * 72, 293 / 25.4 * 72),
      fitz.Point(73 / 25.4 * 72, 293 / 25.4 * 72),
  )
  shape_s4.finish(color=(0, 0, 0), width=1)
  shape_s4.commit()

  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 40. --- Insertion du texte "Duplicata" ---
  texte_duplicata = "Duplicata"
  taille_duplicata = 7.2
  espacement_duplicata = 0

  left_mm_dup = 2
  top_mm_dup = 268.1
  left_pt_dup = left_mm_dup / 25.4 * 72
  top_pt_dup = top_mm_dup / 25.4 * 72

  page.insert_font(fontname="CeraBoldDuplicata", fontfile=police_bold)

  x = left_pt_dup
  y = top_pt_dup + taille_duplicata

  for c in texte_duplicata:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldDuplicata",
        fontsize=taille_duplicata,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_duplicata)
    x += largeur_c + espacement_duplicata

  print("Texte 'Duplicata' inséré dans le PDF.")

  # 41. --- Insertion du texte "1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286" ---
  texte_dup_ref = "1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286"
  taille_dup_ref = 7.2
  espacement_dup_ref = 0

  left_mm_dref = 2
  top_mm_dref = 270.8
  left_pt_dref = left_mm_dref / 25.4 * 72
  top_pt_dref = top_mm_dref / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDuplicataRef", fontfile=police_medium
  )

  x = left_pt_dref
  y = top_pt_dref + taille_dup_ref

  for c in texte_dup_ref:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDuplicataRef",
        fontsize=taille_dup_ref,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_dup_ref)
    x += largeur_c + espacement_dup_ref

  print(
      "Texte '1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286' inséré"
      " dans le PDF."
  )

  # 42. --- Insertion du texte "Système de caisse certifié LNE" ---
  texte_lne = "Système de caisse certifié LNE"
  taille_lne = 7.2
  espacement_lne = 0

  left_mm_lne = 2
  top_mm_lne = 273.1
  left_pt_lne = left_mm_lne / 25.4 * 72
  top_pt_lne = top_mm_lne / 25.4 * 72

  page.insert_font(fontname="CeraMediumLNE", fontfile=police_medium)

  x = left_pt_lne
  y = top_pt_lne + taille_lne

  for c in texte_lne:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLNE",
        fontsize=taille_lne,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_lne)
    x += largeur_c + espacement_lne

  print("Texte 'Système de caisse certifié LNE' inséré dans le PDF.")

  # 43. --- Insertion du texte "LEGO BRAND RETAIL S.A.S est enregistré au Registre" ---
  texte_legal1 = "LEGO BRAND RETAIL S.A.S est enregistré au Registre"
  taille_legal1 = 7.2
  espacement_legal1 = 0

  left_mm_l1_leg = 6.5
  top_mm_l1_leg = 278.5
  left_pt_l1_leg = left_mm_l1_leg / 25.4 * 72
  top_pt_l1_leg = top_mm_l1_leg / 25.4 * 72

  page.insert_font(fontname="CeraMediumLegal1", fontfile=police_medium)

  x = left_pt_l1_leg
  y = top_pt_l1_leg + taille_legal1

  for c in texte_legal1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLegal1",
        fontsize=taille_legal1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_legal1)
    x += largeur_c + espacement_legal1

  print(
      "Texte 'LEGO BRAND RETAIL S.A.S est enregistré au Registre' inséré dans"
      " le PDF."
  )

  # 44. --- Insertion du texte "national des metteurs sur le marché des jeux et jouets sous" ---
  texte_legal2 = "national des metteurs sur le marché des jeux et jouets sous"
  taille_legal2 = 7.2
  espacement_legal2 = 0

  left_mm_leg2 = 2.5
  top_mm_leg2 = 281
  left_pt_leg2 = left_mm_leg2 / 25.4 * 72
  top_pt_leg2 = top_mm_leg2 / 25.4 * 72

  page.insert_font(fontname="CeraMediumLegal2", fontfile=police_medium)

  x = left_pt_leg2
  y = top_pt_leg2 + taille_legal2

  for c in texte_legal2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLegal2",
        fontsize=taille_legal2,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_legal2)
    x += largeur_c + espacement_legal2

  print(
      "Texte 'national des metteurs sur le marché des jeux et jouets sous'"
      " inséré dans le PDF."
  )

  # 45. --- Insertion du texte "le numéro FR214763_12TBLL." ---
  texte_legal3 = "le numéro FR214763_12TBLL."
  taille_legal3 = 7.2
  espacement_legal3 = 0

  left_mm_leg3 = 20.8
  top_mm_leg3 = 283.5
  left_pt_leg3 = left_mm_leg3 / 25.4 * 72
  top_pt_leg3 = top_mm_leg3 / 25.4 * 72

  page.insert_font(fontname="CeraMediumLegal3", fontfile=police_medium)

  x = left_pt_leg3
  y = top_pt_leg3 + taille_legal3

  for c in texte_legal3:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumLegal3",
        fontsize=taille_legal3,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_legal3)
    x += largeur_c + espacement_legal3

  print("Texte 'le numéro FR214763_12TBLL.' inséré dans le PDF.")

  # 46. --- Insertion du titre "Ticket de carte bancaire" ---
  texte_cb_titre = "Ticket de carte bancaire"
  taille_cb_titre = 10.5
  espacement_cb_titre = 0

  left_mm_cb_titre = 2
  top_mm_cb_titre = 295.2
  left_pt_cb_titre = left_mm_cb_titre / 25.4 * 72
  top_pt_cb_titre = top_mm_cb_titre / 25.4 * 72

  page.insert_font(fontname="CeraBoldCBTitre", fontfile=police_bold)

  x = left_pt_cb_titre
  y = top_pt_cb_titre + taille_cb_titre

  for c in texte_cb_titre:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldCBTitre",
        fontsize=taille_cb_titre,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_cb_titre)
    x += largeur_c + espacement_cb_titre

  print("Texte 'Ticket de carte bancaire' inséré dans le PDF.")

  # 47. --- Insertion du texte "Date/Heure" ---
  texte_date = "Date/Heure"
  taille_date = 9.5
  espacement_date = -0.02

  left_mm_date = 2
  top_mm_date = 300.8
  left_pt_date = left_mm_date / 25.4 * 72
  top_pt_date = top_mm_date / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBDate", fontfile=police_medium)

  x = left_pt_date
  y = top_pt_date + taille_date

  for c in texte_date:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBDate",
        fontsize=taille_date,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_date)
    x += largeur_c + espacement_date

  print("Texte 'Date/Heure' inséré dans le PDF.")

  # 48. --- Insertion de la valeur "24/08/2026 19:35:15" ---
  texte_date_valeur = "24/08/2026 19:35:15"
  taille_date_valeur = 9.5
  espacement_date_valeur = -0.1

  left_mm_date_val = 40.8
  top_mm_date_val = 300.8
  left_pt_date_val = left_mm_date_val / 25.4 * 72
  top_pt_date_val = top_mm_date_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCBValeurDate", fontfile=police_medium
  )

  x = left_pt_date_val
  y = top_pt_date_val + taille_date_valeur

  for c in texte_date_valeur:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBValeurDate",
        fontsize=taille_date_valeur,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_date_valeur)
    x += largeur_c + espacement_date_valeur

  print("Texte '24/08/2026 19:35:15' inséré dans le PDF.")

  # 49. --- Insertion du texte "Carte" ---
  texte_carte = "Carte"
  taille_carte = 9.5
  espacement_carte = -0.02

  left_mm_carte = 2
  top_mm_carte = 304
  left_pt_carte = left_mm_carte / 25.4 * 72
  top_pt_carte = top_mm_carte / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBCarte", fontfile=police_medium)

  x = left_pt_carte
  y = top_pt_carte + taille_carte

  for c in texte_carte:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBCarte",
        fontsize=taille_carte,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_carte)
    x += largeur_c + espacement_carte

  print("Texte 'Carte' inséré dans le PDF.")

  # 50. --- Insertion du texte "**** 0777" ---
  texte_numero = "**** 0777"
  taille_numero = 9.5
  espacement_numero = 0

  left_mm_numero = 59
  top_mm_numero = 304
  left_pt_numero = left_mm_numero / 25.4 * 72
  top_pt_numero = top_mm_numero / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBNumero", fontfile=police_medium)

  x = left_pt_numero
  y = top_pt_numero + taille_numero

  for c in texte_numero:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBNumero",
        fontsize=taille_numero,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_numero)
    x += largeur_c + espacement_numero

  print("Texte '**** 0777' inséré dans le PDF.")

  # 51. --- Insertion du texte "Type de carte" ---
  texte_type_carte = "Type de carte"
  taille_type_carte = 9.5
  espacement_type_carte = -0.02

  left_mm_type_carte = 2
  top_mm_type_carte = 307.2
  left_pt_type_carte = left_mm_type_carte / 25.4 * 72
  top_pt_type_carte = top_mm_type_carte / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCBTypeCarte", fontfile=police_medium
  )

  x = left_pt_type_carte
  y = top_pt_type_carte + taille_type_carte

  for c in texte_type_carte:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBTypeCarte",
        fontsize=taille_type_carte,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_type_carte)
    x += largeur_c + espacement_type_carte

  print("Texte 'Type de carte' inséré dans le PDF.")

  # 52. --- Insertion de la valeur "Visa" ---
  texte_visa = "Visa"
  taille_visa = 9.5
  espacement_visa = 0

  left_mm_visa = 66.6
  top_mm_visa = 307.2
  left_pt_visa = left_mm_visa / 25.4 * 72
  top_pt_visa = top_mm_visa / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBVisa", fontfile=police_medium)

  x = left_pt_visa
  y = top_pt_visa + taille_visa

  for c in texte_visa:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBVisa",
        fontsize=taille_visa,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_visa)
    x += largeur_c + espacement_visa

  print("Texte 'Visa' inséré dans le PDF.")

  # 53. --- Insertion du texte "Type de saisie" ---
  texte_type_saisie = "Type de saisie"
  taille_type_saisie = 9.5
  espacement_type_saisie = -0.02

  left_mm_type_saisie = 2
  top_mm_type_saisie = 310.8
  left_pt_type_saisie = left_mm_type_saisie / 25.4 * 72
  top_pt_type_saisie = top_mm_type_saisie / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCBTypeSaisie", fontfile=police_medium
  )

  x = left_pt_type_saisie
  y = top_pt_type_saisie + taille_type_saisie

  for c in texte_type_saisie:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBTypeSaisie",
        fontsize=taille_type_saisie,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_type_saisie)
    x += largeur_c + espacement_type_saisie

  print("Texte 'Type de saisie' inséré dans le PDF.")

  # 54. --- Insertion du texte "Puce sans contact" ---
  texte_puce = "Puce sans contact"
  taille_puce = 9.5
  espacement_puce = 0

  left_mm_puce = 44.7
  top_mm_puce = 310.8
  left_pt_puce = left_mm_puce / 25.4 * 72
  top_pt_puce = top_mm_puce / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBPuce", fontfile=police_medium)

  x = left_pt_puce
  y = top_pt_puce + taille_puce

  for c in texte_puce:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBPuce",
        fontsize=taille_puce,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_puce)
    x += largeur_c + espacement_puce

  print("Texte 'Puce sans contact' inséré dans le PDF.")

  # 55. --- Insertion du texte "AID" ---
  texte_aid = "AID"
  taille_aid = 9.5
  espacement_aid = -0.02

  left_mm_aid = 2
  top_mm_aid = 314.2
  left_pt_aid = left_mm_aid / 25.4 * 72
  top_pt_aid = top_mm_aid / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBAID", fontfile=police_medium)

  x = left_pt_aid
  y = top_pt_aid + taille_aid

  for c in texte_aid:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBAID",
        fontsize=taille_aid,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_aid)
    x += largeur_c + espacement_aid

  print("Texte 'AID' inséré dans le PDF.")

  # 56. --- Insertion de la valeur "A0000000031010" ---
  texte_aid_valeur = "A0000000031010"
  taille_aid_valeur = 9.5
  espacement_aid_valeur = 0

  left_mm_aid_val = 45.5
  top_mm_aid_val = 314.2
  left_pt_aid_val = left_mm_aid_val / 25.4 * 72
  top_pt_aid_val = top_mm_aid_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCBAIDValeur", fontfile=police_medium
  )

  x = left_pt_aid_val
  y = top_pt_aid_val + taille_aid_valeur

  for c in texte_aid_valeur:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBAIDValeur",
        fontsize=taille_aid_valeur,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_aid_valeur)
    x += largeur_c + espacement_aid_valeur

  print("Texte 'A0000000031010' inséré dans le PDF.")

  # 57. --- Insertion du texte "Code d'autor." ---
  texte_autor = "Code d'autor."
  taille_autor = 9.5
  espacement_autor = -0.02

  left_mm_autor = 2
  top_mm_autor = 317.3
  left_pt_autor = left_mm_autor / 25.4 * 72
  top_pt_autor = top_mm_autor / 25.4 * 72

  page.insert_font(fontname="CeraMediumCBAutor", fontfile=police_medium)

  x = left_pt_autor
  y = top_pt_autor + taille_autor

  for c in texte_autor:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBAutor",
        fontsize=taille_autor,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_autor)
    x += largeur_c + espacement_autor

  print("Texte 'Code d\\'autor.' inséré dans le PDF.")

  # 58. --- Insertion de la valeur "056013" ---
  texte_autor_valeur = "056013"
  taille_autor_valeur = 9.5
  espacement_autor_valeur = 0

  left_mm_autor_val = 62
  top_mm_autor_val = 317.3
  left_pt_autor_val = left_mm_autor_val / 25.4 * 72
  top_pt_autor_val = top_mm_autor_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumCBAutorValeur", fontfile=police_medium
  )

  x = left_pt_autor_val
  y = top_pt_autor_val + taille_autor_valeur

  for c in texte_autor_valeur:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumCBAutorValeur",
        fontsize=taille_autor_valeur,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_autor_valeur)
    x += largeur_c + espacement_autor_valeur

  print("Texte '056013' inséré dans le PDF.")

  # 59. --- Insertion de la ligne de séparation vectorielle (1) ---
  left_mm_ligne = 2.2
  right_mm_ligne = 73
  top_mm_ligne = 324.8
  epaisseur_ligne = 1.3

  x0 = left_mm_ligne / 25.4 * 72
  x1 = right_mm_ligne / 25.4 * 72
  y_ligne = top_mm_ligne / 25.4 * 72

  shape = page.new_shape()
  shape.draw_line(fitz.Point(x0, y_ligne), fitz.Point(x1, y_ligne))
  shape.finish(color=(0, 0, 0), width=epaisseur_ligne)
  shape.commit()

  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 60. --- Insertion de l'image "width87.png" ---
  largeur_w87_mm = 13.8
  left_w87_mm = 59
  top_w87_mm = 328

  left_w87_pt = left_w87_mm / 25.4 * 72
  top_w87_pt = top_w87_mm / 25.4 * 72
  largeur_w87_pt = largeur_w87_mm / 25.4 * 72

  img_w87_doc = fitz.open(image_width87_path)
  ratio_w87 = img_w87_doc[0].rect.height / img_w87_doc[0].rect.width
  hauteur_w87_pt = largeur_w87_pt * ratio_w87

  rect_w87 = fitz.Rect(
      left_w87_pt,
      top_w87_pt,
      left_w87_pt + largeur_w87_pt,
      top_w87_pt + hauteur_w87_pt,
  )
  page.insert_image(rect_w87, filename=image_width87_path)

  print("Image 'width87.png' insérée dans le PDF.")

  # 61. --- Insertion du titre "Détails de la commande" ---
  texte_details = "Détails de la commande"
  taille_details = 10.5
  espacement_details = 0

  left_mm_det = 2
  top_mm_det = 327.3
  left_pt_det = left_mm_det / 25.4 * 72
  top_pt_det = top_mm_det / 25.4 * 72

  page.insert_font(
      fontname="CeraBoldDetailsCommande", fontfile=police_bold
  )

  x = left_pt_det
  y = top_pt_det + taille_details

  for c in texte_details:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldDetailsCommande",
        fontsize=taille_details,
        color=(0, 0, 0),
    )
    largeur_c = font_bold.text_length(c, fontsize=taille_details)
    x += largeur_c + espacement_details

  print("Texte 'Détails de la commande' inséré dans le PDF.")

  # 62. --- Insertion du texte "Transaction n°:" ---
  texte_trans_label = "Transaction n°:"
  taille_trans_label = 8
  espacement_trans_label = -0.02

  left_mm_t_lab = 2
  top_mm_t_lab = 332.8
  left_pt_t_lab = left_mm_t_lab / 25.4 * 72
  top_pt_t_lab = top_mm_t_lab / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDetailsTransaction", fontfile=police_medium
  )

  x = left_pt_t_lab
  y = top_pt_t_lab + taille_trans_label

  for c in texte_trans_label:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDetailsTransaction",
        fontsize=taille_trans_label,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_trans_label)
    x += largeur_c + espacement_trans_label

  print("Texte 'Transaction n°:' inséré dans le PDF.")

  # 63. --- Insertion de la valeur "LEGO0064863689" ---
  texte_trans_val = "LEGO0064863689"
  taille_trans_val = 8
  espacement_trans_val = -0.02

  left_mm_t_val = 30.5
  top_mm_t_val = 332.8
  left_pt_t_val = left_mm_t_val / 25.4 * 72
  top_pt_t_val = top_mm_t_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDetailsTransactionValeur", fontfile=police_medium
  )

  x = left_pt_t_val
  y = top_pt_t_val + taille_trans_val

  for c in texte_trans_val:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDetailsTransactionValeur",
        fontsize=taille_trans_val,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_trans_val)
    x += largeur_c + espacement_trans_val

  print("Texte 'LEGO0064863689' inséré dans le PDF.")

  # 64. --- Insertion du texte "Date et heure:" ---
  texte_date_label = "Date et heure:"
  taille_date_label = 8
  espacement_date_label = -0.02

  left_mm_d_lab = 2
  top_mm_d_lab = 335.3
  left_pt_d_lab = left_mm_d_lab / 25.4 * 72
  top_pt_d_lab = top_mm_d_lab / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDetailsDateLabel", fontfile=police_medium
  )

  x = left_pt_d_lab
  y = top_pt_d_lab + taille_date_label

  for c in texte_date_label:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDetailsDateLabel",
        fontsize=taille_date_label,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_date_label)
    x += largeur_c + espacement_date_label

  print("Texte 'Date et heure:' inséré dans le PDF.")

  # 65. --- Insertion du texte "24 août 2026" ---
  texte_date_val = "24 août 2026"
  taille_date_val = 8
  espacement_date_val = -0.02

  left_mm_d_val = 30.5
  top_mm_d_val = 335.3
  left_pt_d_val = left_mm_d_val / 25.4 * 72
  top_pt_d_val = top_mm_d_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDetailsDateValeur", fontfile=police_medium
  )

  x = left_pt_d_val
  y = top_pt_d_val + taille_date_val

  for c in texte_date_val:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDetailsDateValeur",
        fontsize=taille_date_val,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_date_val)
    x += largeur_c + espacement_date_val

  print("Texte '24 août 2026' inséré dans le PDF.")

  # 66. --- Insertion du texte "19:35:15" ---
  texte_heure_val = "19:35:15"
  taille_heure_val = 8
  espacement_heure_val = -0.02

  left_mm_h_val = 30.4
  top_mm_h_val = 338.2
  left_pt_h_val = left_mm_h_val / 25.4 * 72
  top_pt_h_val = top_mm_h_val / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumDetailsHeureValeur", fontfile=police_medium
  )

  x = left_pt_h_val
  y = top_pt_h_val + taille_heure_val

  for c in texte_heure_val:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumDetailsHeureValeur",
        fontsize=taille_heure_val,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_heure_val)
    x += largeur_c + espacement_heure_val

  print("Texte '19:35:15' inséré dans le PDF.")

  # 67. --- Insertion de la ligne de séparation vectorielle (2) ---
  left_mm_ligne2 = 2.2
  right_mm_ligne2 = 73
  top_mm_ligne2 = 345
  epaisseur_ligne2 = 1

  x0_2 = left_mm_ligne2 / 25.4 * 72
  x1_2 = right_mm_ligne2 / 25.4 * 72
  y_ligne2 = top_mm_ligne2 / 25.4 * 72

  shape2 = page.new_shape()
  shape2.draw_line(fitz.Point(x0_2, y_ligne2), fitz.Point(x1_2, y_ligne2))
  shape2.finish(color=(0, 0, 0), width=epaisseur_ligne2)
  shape2.commit()

  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 68. --- Insertion du texte de garantie (L1) ---
  texte_g1 = "Ce bien bénéficie auprès du vendeur d’une garantie"
  taille_g1 = 8
  espacement_g1 = -0.02

  left_mm_g1 = 3.3
  top_mm_g1 = 347.8
  left_pt_g1 = left_mm_g1 / 25.4 * 72
  top_pt_g1 = top_mm_g1 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumGarantieL1", fontfile=police_medium
  )

  x = left_pt_g1
  y = top_pt_g1 + taille_g1

  for c in texte_g1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumGarantieL1",
        fontsize=taille_g1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_g1)
    x += largeur_c + espacement_g1

  print("Texte 'Ce bien bénéficie auprès du vendeur d’une garantie' inséré dans le PDF.")

  # 69. --- Insertion du texte de garantie (L2) ---
  texte_g2 = "légale de conformité d’une durée de deux ans à"
  taille_g2 = 8
  espacement_g2 = -0.02

  left_mm_g2 = 6
  top_mm_g2 = 350.8
  left_pt_g2 = left_mm_g2 / 25.4 * 72
  top_pt_g2 = top_mm_g2 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumGarantieL2", fontfile=police_medium
  )

  x = left_pt_g2
  y = top_pt_g2 + taille_g2

  for c in texte_g2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumGarantieL2",
        fontsize=taille_g2,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_g2)
    x += largeur_c + espacement_g2

  print("Texte 'légale de conformité d’une durée de deux ans à' inséré dans le PDF.")

  # 70. --- Insertion du texte de garantie (L3) ---
  texte_g3 = "compter de sa remise au consommateur."
  taille_g3 = 8
  espacement_g3 = -0.02

  left_mm_g3 = 10.7
  top_mm_g3 = 353.5
  left_pt_g3 = left_mm_g3 / 25.4 * 72
  top_pt_g3 = top_mm_g3 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumGarantieL3", fontfile=police_medium
  )

  x = left_pt_g3
  y = top_pt_g3 + taille_g3

  for c in texte_g3:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumGarantieL3",
        fontsize=taille_g3,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_g3)
    x += largeur_c + espacement_g3

  print("Texte 'compter de sa remise au consommateur.' inséré dans le PDF.")

  # 71. --- Insertion de la ligne de séparation vectorielle (3) ---
  left_mm_ligne3 = 2.2
  right_mm_ligne3 = 73
  top_mm_ligne3 = 360.2
  epaisseur_ligne3 = 1.3

  x0_3 = left_mm_ligne3 / 25.4 * 72
  x1_3 = right_mm_ligne3 / 25.4 * 72
  y_ligne3 = top_mm_ligne3 / 25.4 * 72

  shape3 = page.new_shape()
  shape3.draw_line(fitz.Point(x0_3, y_ligne3), fitz.Point(x1_3, y_ligne3))
  shape3.finish(color=(0, 0, 0), width=epaisseur_ligne3)
  shape3.commit()

  print("Nouvelle ligne de séparation vectorielle insérée dans le PDF.")

  # 72. --- Insertion du texte "LEGO Brand Retail SAS" ---
  texte_ret1 = "LEGO Brand Retail SAS"
  taille_ret1 = 8
  espacement_ret1 = -0.02

  left_mm_ret1 = 22.5
  top_mm_ret1 = 365.8
  left_pt_ret1 = left_mm_ret1 / 25.4 * 72
  top_pt_ret1 = top_mm_ret1 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumRetailL1", fontfile=police_medium
  )

  x = left_pt_ret1
  y = top_pt_ret1 + taille_ret1

  for c in texte_ret1:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumRetailL1",
        fontsize=taille_ret1,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ret1)
    x += largeur_c + espacement_ret1

  print("Texte 'LEGO Brand Retail SAS' inséré dans le PDF.")

  # 73. --- Insertion du texte "75 rue de Tocqueville," ---
  texte_ret2 = "75 rue de Tocqueville,"
  taille_ret2 = 8
  espacement_ret2 = -0.02

  left_mm_ret2 = 23.2
  top_mm_ret2 = 368.8
  left_pt_ret2 = left_mm_ret2 / 25.4 * 72
  top_pt_ret2 = top_mm_ret2 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumRetailL2", fontfile=police_medium
  )

  x = left_pt_ret2
  y = top_pt_ret2 + taille_ret2

  for c in texte_ret2:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumRetailL2",
        fontsize=taille_ret2,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ret2)
    x += largeur_c + espacement_ret2

  print("Texte '75 rue de Tocqueville,' inséré dans le PDF.")

  # 74. --- Insertion du texte "75017 Paris, FR" ---
  texte_ret3 = "75017 Paris, FR"
  taille_ret3 = 8
  espacement_ret3 = -0.02

  left_mm_ret3 = 28
  top_mm_ret3 = 371.5
  left_pt_ret3 = left_mm_ret3 / 25.4 * 72
  top_pt_ret3 = top_mm_ret3 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumRetailL3", fontfile=police_medium
  )

  x = left_pt_ret3
  y = top_pt_ret3 + taille_ret3

  for c in texte_ret3:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumRetailL3",
        fontsize=taille_ret3,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ret3)
    x += largeur_c + espacement_ret3

  print("Texte '75017 Paris, FR' inséré dans le PDF.")

  # 75. --- Insertion du texte "FR 61752526178" ---
  texte_ret4 = "FR 61752526178"
  taille_ret4 = 8
  espacement_ret4 = -0.02

  left_mm_ret4 = 27.4
  top_mm_ret4 = 374.2
  left_pt_ret4 = left_mm_ret4 / 25.4 * 72
  top_pt_ret4 = top_mm_ret4 / 25.4 * 72

  page.insert_font(
      fontname="CeraMediumRetailL4", fontfile=police_medium
  )

  x = left_pt_ret4
  y = top_pt_ret4 + taille_ret4

  for c in texte_ret4:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumRetailL4",
        fontsize=taille_ret4,
        color=(0, 0, 0),
    )
    largeur_c = font_medium.text_length(c, fontsize=taille_ret4)
    x += largeur_c + espacement_ret4

  print("Texte 'FR 61752526178' inséré dans le PDF.")

  # --- Mise à jour du titre du document (Métadonnées) ---
  meta = doc.metadata
  meta["title"] = "Receipt"
  doc.set_metadata(meta)

  doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
  doc.close()
  print("Génération complète et fusion réussie !")


if __name__ == "__main__":
  executer_generation_complete()