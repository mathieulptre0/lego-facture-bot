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
  dossier = os.path.dirname(__file__)
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

  # DUPLICATA (Haut)
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
  largeur_w60_mm = 19
  left_w60_pt = 28 / 25.4 * 72
  top_w60_pt = 15.3 / 25.4 * 72
  largeur_w60_pt = largeur_w60_mm / 25.4 * 72
  img_w60_doc = fitz.open(image_width60_path)
  hauteur_w60_pt = (
      largeur_w60_pt * (img_w60_doc[0].rect.height / img_w60_doc[0].rect.width)
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

  # Adresses
  for texte, t_sz, esp, l_mm, t_mm, fname in [
      ("149 LEGO, LQT Paris, EU-FR", 7.9, 0.03, 20, 40.4, "CeraMediumLQT"),
      ("15 Parv. de la Défense,", 7.9, 0, 23, 43.2, "CeraMedium2"),
      ("92092 Puteaux, FR", 7.9, 0, 25.5, 46.2, "CeraMedium3"),
  ]:
    page.insert_font(fontname=fname, fontfile=police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + t_sz
    for c in texte:
      page.insert_text((x, y), c, fontname=fname, fontsize=t_sz, color=(0, 0, 0))
      x += font_medium.text_length(c, fontsize=t_sz) + esp

  # Transaction de vente
  texte_trans = "Transaction de vente"
  taille_trans = 15
  x, y = 11 / 25.4 * 72, (54.5 / 25.4 * 72) + taille_trans
  page.insert_font(fontname="CeraBoldTrans", fontfile=police_bold)
  for c in texte_trans:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraBoldTrans",
        fontsize=taille_trans,
        color=(0, 0, 0),
    )
    x += font_bold.text_length(c, fontsize=taille_trans)

  # Article & Prix
  taille_article = 9.5
  x, y = 2 / 25.4 * 72, (66 / 25.4 * 72) + taille_article
  page.insert_font(fontname="CeraMediumArt1", fontfile=police_medium)
  for c in item_name:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumArt1",
        fontsize=taille_article,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=taille_article)

  right_pt_p1 = 72.5 / 25.4 * 72
  largeur_totale_p1 = sum(
      font_medium.text_length(c, fontsize=9.5) for c in item_price
  )
  x, y = right_pt_p1 - largeur_totale_p1, (66 / 25.4 * 72) + 9.5
  page.insert_font(fontname="CeraMediumPrix1", fontfile=police_medium)
  for c in item_price:
    page.insert_text(
        (x, y),
        c,
        fontname="CeraMediumPrix1",
        fontsize=9.5,
        color=(0, 0, 0),
    )
    x += font_medium.text_length(c, fontsize=9.5)

  # TVA & Totaux
  for texte, t_sz, l_mm, t_mm, fname, is_b in [
      ("Récapitulatif TVA  Taux", 9.3, 2.2, 73.6, "CeraMediumTVA", False),
      ("TVA", 9.2, 66.5, 73.7, "CeraMediumTVATexte", False),
      ("20.0%", 9.3, 30.8, 77.8, "CeraMedium20", False),
      ("Total", 9.3, 30.8, 81.5, "CeraMediumTotalLabel", False),
      ("Nombre d'articles : 1", 9.5, 2.2, 91, "CeraMediumNbArticles", False),
      ("Total à payer", 11, 2.1, 96.5, "CeraBoldTotalPayer", True),
      ("Payé avec Visa", 9.5, 2.1, 106.5, "CeraMediumVisa", False),
  ]:
    page.insert_font(
        fontname=fname, fontfile=police_bold if is_b else police_medium
    )
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + t_sz
    for c in texte:
      page.insert_text((x, y), c, fontname=fname, fontsize=t_sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=t_sz)

  # Montants TVA et Prix alignés à droite
  for montant, top_mm in [
      (tva_price, 77.6),
      (item_price, 81.4),
      (item_price, 96.5),
      (item_price, 106.5),
  ]:
    right_pt = 72.7 / 25.4 * 72
    largeur = sum(font_medium.text_length(c, fontsize=9.5) for c in montant)
    x, y = right_pt - largeur, (top_mm / 25.4 * 72) + 9.5
    page.insert_font(fontname=f"Font_{top_mm}", fontfile=police_medium)
    for c in montant:
      page.insert_text(
          (x, y), c, fontname=f"Font_{top_mm}", fontsize=9.5, color=(0, 0, 0)
      )
      x += font_medium.text_length(c, fontsize=9.5)

  # Images Avis & QR code
  for img_path, l_mm, t_mm, w_mm in [
      (image_avis_path, 0.6, 120.3, 74),
      (image_width99_path, 23.7, 124.5, 14),
  ]:
    l_pt, t_pt, w_pt = (
        l_mm / 25.4 * 72,
        t_mm / 25.4 * 72,
        w_mm / 25.4 * 72,
    )
    im_doc = fitz.open(img_path)
    h_pt = w_pt * (im_doc[0].rect.height / im_doc[0].rect.width)
    page.insert_image(
        fitz.Rect(l_pt, t_pt, l_pt + w_pt, t_pt + h_pt), filename=img_path
    )

  # Blocs de texte d'avis & Code d'avis dynamique
  for texte, t_sz, l_mm, t_mm, fname, is_b in [
      ("Comment jugez-", 10.5, 39.8, 124.7, "CeraBoldJuger", True),
      ("vous votre", 10.4, 39.8, 129, "CeraBoldVousVotre", True),
      ("expérience ?", 10.4, 39.8, 133.2, "CeraBoldExperience", True),
      (
          "Sinon, répondez en 3 minutes à notre",
          8,
          23.6,
          143.8,
          "CeraMediumSinon",
          False,
      ),
      (
          "questionnaire sur LEGO.com/",
          8,
          23.6,
          146.5,
          "CeraMediumQuestionnaire",
          False,
      ),
      ("storesurvey", 8, 23.5, 149.3, "CeraMediumStoreSurvey", False),
      ("Au besoin, utilisez ce code :", 8, 23.5, 154.2, "CeraMediumAuBesoin", False),
      (code_besoin, 8, 23.5, 157, "CeraMediumCodeBesoin", False),
  ]:
    page.insert_font(
        fontname=fname, fontfile=police_bold if is_b else police_medium
    )
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + t_sz
    for c in texte:
      page.insert_text((x, y), c, fontname=fname, fontsize=t_sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=t_sz)

  # Lignes de séparation
  for y_m in [168, 196.2, 216.2, 293, 324.8, 345, 360.2]:
    shape = page.new_shape()
    shape.draw_line(
        fitz.Point(2.2 / 25.4 * 72, y_m / 25.4 * 72),
        fitz.Point(73 / 25.4 * 72, y_m / 25.4 * 72),
    )
    shape.finish(
        color=(0, 0, 0), width=1.3 if y_m in [216.2, 324.8, 360.2] else 1
    )
    shape.commit()

  # Insiders, abonnements et mentions légales
  for txt, sz, l_mm, t_mm, fname, is_b in [
      ("Deviens un LEGO® Insider !", 10.5, 14, 170.8, "CeraBoldInsider", True),
      (
          "Rejoins le programme LEGO® Insiders pour",
          9.7,
          4,
          177.2,
          "CeraMediumInsider1",
          False,
      ),
      (
          "profiter de formidables avantages et",
          9.7,
          4,
          180.7,
          "CeraMediumInsider2",
          False,
      ),
      ("récompenses LEGO®", 9.7, 4, 184, "CeraMediumInsider3", False),
      ("LEGO.com/insiders", 9.7, 4, 189, "CeraMediumInsiderUrl", False),
      ("S'abonner aux e-mails", 10.5, 18.3, 198.8, "CeraBoldAbonner", True),
      (
          "Suivez notre actualité en vous abonnant à",
          9.5,
          4.8,
          205.5,
          "CeraMediumAbonner1",
          False,
      ),
      (
          "notre programme d'e-mails LEGO.com/email",
          9.5,
          4.8,
          208.8,
          "CeraMediumAbonner2",
          False,
      ),
      ("Caractéristiques de sécurité", 10.5, 12.9, 218.8, "CeraBoldSecurite", True),
      ("Duplicata", 7.2, 2, 268.1, "CeraBoldDuplicata", True),
      (
          "1. Duplicata de 7fd15f69-a829-4946-b76d-fe8c93929286",
          7.2,
          2,
          270.8,
          "CeraMediumDuplicataRef",
          False,
      ),
      ("Système de caisse certifié LNE", 7.2, 2, 273.1, "CeraMediumLNE", False),
      (
          "LEGO BRAND RETAIL S.A.S est enregistré au Registre",
          7.2,
          2,
          278.5,
          "CeraMediumLegal1",
          False,
      ),
      (
          "national des metteurs sur le marché des jeux et jouets sous",
          7.2,
          2,
          281,
          "CeraMediumLegal2",
          False,
      ),
      ("le numéro FR214763_12TBLL.", 7.2, 2, 283.5, "CeraMediumLegal3", False),
  ]:
    page.insert_font(
        fontname=fname, fontfile=police_bold if is_b else police_medium
    )
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # Image width200 & width87
  for img_path, l_mm, t_mm, w_mm in [
      (image_width200_path, 18.4, 228.8, 38.1),
      (image_width87_path, 59, 328, 13.8),
  ]:
    l_pt, t_pt, w_pt = (
        l_mm / 25.4 * 72,
        t_mm / 25.4 * 72,
        w_mm / 25.4 * 72,
    )
    im_doc = fitz.open(img_path)
    h_pt = w_pt * (im_doc[0].rect.height / im_doc[0].rect.width)
    page.insert_image(
        fitz.Rect(l_pt, t_pt, l_pt + w_pt, t_pt + h_pt), filename=img_path
    )

  # Carte bancaire et détails de fin dynamiques
  for txt, sz, l_mm, t_mm, fname, is_b in [
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
      ("Détails de la commande", 10.5, 2, 327.3, "CeraBoldDetailsCommande", True),
      ("Transaction n°:", 8, 2, 332.8, "CeraMediumDetailsTransaction", False),
      (
          "LEGO0064863689",
          8,
          30.5,
          332.8,
          "CeraMediumDetailsTransactionValeur",
          False,
      ),
      ("Date et heure:", 8, 2, 335.3, "CeraMediumDetailsDateLabel", False),
      (date_long, 8, 30.5, 335.3, "CeraMediumDetailsDateValeur", False),
      (heure, 8, 30.4, 338.2, "CeraMediumDetailsHeureValeur", False),
  ]:
    page.insert_font(
        fontname=fname, fontfile=police_bold if is_b else police_medium
    )
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += (font_bold if is_b else font_medium).text_length(c, fontsize=sz)

  # Pied de page final
  for txt, sz, l_mm, t_mm, fname in [
      (
          "Ce bien bénéficie auprès du vendeur d’une garantie",
          8,
          3.3,
          347.8,
          "CeraMediumGarantieL1",
      ),
      (
          "légale de conformité d’une durée de deux ans à",
          8,
          6,
          350.8,
          "CeraMediumGarantieL2",
      ),
      ("compter de sa remise au consommateur.", 8, 10.7, 353.5, "CeraMediumGarantieL3"),
      ("LEGO Brand Retail SAS", 8, 22.5, 365.8, "CeraMediumRetailL1"),
      ("75 rue de Tocqueville,", 8, 23.2, 368.8, "CeraMediumRetailL2"),
      ("75017 Paris, FR", 8, 28, 371.5, "CeraMediumRetailL3"),
      ("FR 61752526178", 8, 27.4, 374.2, "CeraMediumRetailL4"),
  ]:
    page.insert_font(fontname=fname, fontfile=police_medium)
    x, y = l_mm / 25.4 * 72, (t_mm / 25.4 * 72) + sz
    for c in txt:
      page.insert_text((x, y), c, fontname=fname, fontsize=sz, color=(0, 0, 0))
      x += font_medium.text_length(c, fontsize=sz)

  meta = doc.metadata
  meta["title"] = "Receipt"
  doc.set_metadata(meta)
  doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
  doc.close()