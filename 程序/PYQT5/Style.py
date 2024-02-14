WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
BUTTON_BAR_HEIGHT = 200


BUTTON_STYLE = """
        QPushButton {
            background-color: White; 
            color : Black;
            border-width: 4px;
            border-radius: 20px;
        }
        QPushButton:hover {
            color: white;
            background-color: darkgreen
        }
    """ 
BUTTON_STYLE_RED = """
        QPushButton {
            background-color: Gray; 
            color : white;
            border-width: 4px;
            border-radius: 20px;
        }
        QPushButton:hover {
            color: white;
            background-color: red
        }
    """ 
SLIDER_STYLE = """
            QSlider::groove:horizontal {
                height: 10px;
                border: 1px solid #bbb;
                background: white;
                margin: 0px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #45ADED, stop:1 #00579A);
                border: 1px solid #5c5c5c;
                width: 15px;
                margin: -2px 0;
                border-radius: 3px;
            }

            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #B1CC00, stop:1 #7D8B00);
                height: 10px;
            }

            QSlider::add-page:horizontal {
                background: #fff;
                height: 10px;
            }

            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #78AADB, stop:1 #00579A);
                border: 1px solid #00579A;
            }

            QSlider::sub-page:horizontal:disabled {
                background: #bbb;
                border-color: #999;
            }

            QSlider::add-page:horizontal:disabled {
                background: #eee;
                border-color: #999;
            }

            QSlider::handle:horizontal:disabled {
                background: #eee;
                border: 1px solid #aaa;
            }

            QSlider::tick:horizontal {
                height: 0px;
            }
            """


SLIDER_STYLE_2 = """
                .QSlider {
                    min-height: 68px;
                    max-height: 68px;
               
                }

                .QSlider::groove:horizontal {
                 
                    height: 5px;
                    background: white;
                    
                }

                .QSlider::handle:horizontal {
                    background: Darkgreen;
                    width: 23px;
                    height: 100px;
                    margin: -24px -12px;
                  
                }
                            }
        """

RADIO_STYLE = """
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 30px;
                height: 30px;
            }
        """

NUM_BUTTON_WIDTH = 200
NUM_BUTTON_HEIGHT = 100