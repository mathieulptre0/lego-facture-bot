import os
import pymupdf as fitz


def generer_ticket_pdf(
    nom_article,
    prix_article_str,
    date_valeur,
    date_lettre,
    heure_valeur,
    code_avis,
    tva_str,
):
  # Chemins des fichiers
  dossier = r"C:\Users\leazy\Desktop\lego facture bot"
  html_path = os.path.join(dossier, "page_blanche.html")
  pdf_path = os.path.join(dossier, "Receipt.pdf")

  # Polices et images
  police_medium = os.path.join(dossier, "CeraProMedium.ttf")
  police_bold = os.path.join(dossier, "cera-pro-bold.ttf")
  image_avis_path = os.path.join(
      dossier, "73b318fc-9648-420d-b3f8-4728ee3156ee.png"
  )
  image_width200_path = os.path.join(dossier, "width200.png")
  image_width87_path = os.path.join(dossier, "width87.png")
  image_width60_path = os.path.join(dossier, "width60.png")
  image_width99_path = os.path.join(dossier, "width99.png")

  # HTML injecté avec les variables dynamiques
  html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family: 'CeraProMedium';
                src: url('{police_medium}');
            }}
            @font-face {{
                font-family: 'CeraProBold';
                src: url('{police_bold}');
            }}
            body {{
                font-family: 'CeraProMedium', Arial, sans-serif;
                margin: 0;
                padding: 40px;
                background-color: #ffffff;
                color: #000000;
            }}
            .container {{
                max-width: 400px;
                margin: 0 auto;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .item-row {{
                display: flex;
                justify-content: space-between;
                margin: 10px 0;
                font-size: 14px;
            }}
            .bold {{
                font-family: 'CeraProBold', Arial, sans-serif;
            }}
            .total {{
                font-size: 16px;
                margin-top: 15px;
                border-top: 1px solid #000;
                padding-top: 10px;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                margin-top: 30px;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>LEGO STORE</h2>
                <p>{date_lettre} - {heure_valeur}</p>
            </div>
            
            <div class="item-row">
                <span>{nom_article}</span>
                <span>{prix_article_str}</span>
            </div>
            
            <div class="item-row total bold">
                <span>TOTAL</span>
                <span>{prix_article_str}</span>
            </div>
            
            <div class="item-row" style="font-size: 12px; margin-top: 20px;">
                <span>TVA incluse (20%)</span>
                <span>{tva_str}</span>
            </div>

            <div class="footer">
                <p>Code d'avis : {code_avis}</p>
                <p>Date technique : {date_valeur}</p>
                <p>Merci de votre visite !</p>
            </div>
        </div>
    </body>
    </html>
    """

  with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

  doc = fitz.open()
  page = doc.new_page(width=595, height=842)

  rect = fitz.Rect(50, 50, 545, 792)
  page.insert_htmlbox(rect, html_content)

  doc.save(pdf_path)
  doc.close()

  return pdf_path