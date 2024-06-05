import json
import urllib.parse
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from io import BytesIO
import base64
from TopColors import TopColors
import numpy as np
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'jkhgfdstryfghkjlk;l'
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ImageDatabase.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db
db = SQLAlchemy(app)


class Images(db.Model):
    __tablename__ = 'Image Data'

    id = db.Column(db.Integer(), primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    b64_image = db.Column(db.Text(), nullable=False)
    top_colors = db.Column(db.Text(), nullable=False)

    def __init__(self, filename, b64_img, top_colors):
        self.filename = filename
        self.b64_image = b64_img
        self.top_colors = json.dumps(top_colors)

    def get_top_colors(self):
        return json.loads(self.top_colors)

    def __repr__(self):
        return f'image : {self.filename}'


# # create db
# db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':

        image = request.files['file']
        img_name_without_ext = image.filename.split('.')[0]

        # Read image using PIL and convert to RGB if necessary
        pil_image = Image.open(BytesIO(image.read())).convert('RGB')
        image_np = np.array(pil_image)

        # converts image to base64 encoded image and save it locally
        image.seek(0)
        base64_img = base64.b64encode(image.read()).decode('utf-8')
        # Gets top 10 colors from image
        colors = TopColors().get_top_colors(image=image_np)

        # checking if the image already exists
        image_exists = Images.query.filter_by(b64_image=base64_img).first()
        if image_exists:
            query_params = {'id': image_exists.id}
        else:
            new_img = Images(
                filename=img_name_without_ext,
                b64_img=base64_img,
                top_colors=colors
            )
            db.session.add(new_img)
            db.session.commit()
            print(f'id of new image : {new_img.id}')
            query_params = {'id': new_img.id}

        query_string = urllib.parse.urlencode(query_params)
        return redirect(url_for('color') + '?' + query_string)
    return render_template('index.html')


@app.route('/color')
def color():
    image_id = request.args.get('id')
    image = Images.query.filter_by(id=image_id).first()
    colors = image.get_top_colors()

    return render_template('color.html', image=image)


if __name__ == '__main__':
    app.run(debug=True)
