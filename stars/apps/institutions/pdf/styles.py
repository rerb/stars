from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.colors import Color
from reportlab.lib.units import inch

blue = Color(.21, .37, .56, 1)
dark_blue = Color(.09, .21, .36, 1)

def getSTARSStyleSheet():
    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName='Times-Roman',
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='Category',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  spaceBefore=6,
                                  spaceAfter=6,
                                  textColor=dark_blue,
                                  fontSize=20,
                                  leading=50)
                   )
                   
    stylesheet.add(ParagraphStyle(name='Subcategory',
                                  parent=stylesheet['Category'],
                                  fontSize=16,
                                  leading=50,
                                    leftIndent=inch/6,
                                  textColor=blue),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Credit',
                                  parent=stylesheet['Category'],
                                  fontName = 'Times-Roman',
                                  fontSize=13,
                                  leftIndent=inch/3),
                   alias='title')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=14,
                                  leading=18,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h2')

    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontSize=12,
                                  leading=14,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Heading4',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-BoldItalic',
                                  fontSize=10,
                                  leading=12,
                                  spaceBefore=10,
                                  spaceAfter=4),
                   alias='h4')

    stylesheet.add(ParagraphStyle(name='Heading5',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=9,
                                  leading=10.8,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h5')

    stylesheet.add(ParagraphStyle(name='Heading6',
                                  parent=stylesheet['Normal'],
                                  fontName = 'Times-Bold',
                                  fontSize=7,
                                  leading=8.4,
                                  spaceBefore=6,
                                  spaceAfter=2),
                   alias='h6')

    stylesheet.add(ParagraphStyle(name='Bullet',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  spaceBefore=3),
                   alias='bu')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceBefore=6,
                                  bulletFontName='Times-BoldItalic'),
                   alias='df')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leading=8.8,
                                  firstLineIndent=0,
                                  leftIndent=36))


    return stylesheet
