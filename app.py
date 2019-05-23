# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import requests
import pymongo
from pymongo import MongoClient
import random
import string

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

client = MongoClient(
    'mongodb://admin:password@127.0.0.1:27017/admin')
db = client['admin']
recipesCol = db.recipes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

deleteButtons = []

def serve_layout():
    return html.Div(className='flex', children=[
        html.Div(className='flex-wide', children=[
            html.Div(id='user-recipe-placeholder', className='recipe'),
            html.Form(id='add-recipe-form', children=[
                html.Label('Название', htmlFor='recipe-title'),
                dcc.Input(
                    placeholder='Омлет',
                    type='text',
                    id='recipe-title',
                    required=True
                ),
                html.Label('Ссылка на изображение',
                           htmlFor='recipe-image'),
                dcc.Input(
                    placeholder='htttp://example.com/?img=123',
                    type='text',
                    value='',
                    id='recipe-image'
                ),
                html.Label('Количество порций', htmlFor='recipe-portions'),
                dcc.Input(
                    placeholder='4',
                    min='1',
                    max='20',
                    type='number',
                    value='',
                    id='recipe-portions',
                        required=True
                ),
                html.Label('Время приготовления (в минутах)',
                           htmlFor='recipe-time'),
                dcc.Input(
                    placeholder='30',
                    type='number',
                    min='1',
                    max='1000',
                    value='',
                    id='recipe-time',
                    required=True
                ),
                html.Label('Ингредиенты',
                           htmlFor='recipe-ingredients'),
                dcc.Textarea(
                    placeholder='Яйца - 4 штуки\nМолоко - 1 литр',
                    value='',
                    id='recipe-ingredients',
                    required=True
                ),
                html.Label('Рецепт',
                           htmlFor='recipe-steps'),
                dcc.Textarea(
                    placeholder='1. Разбить яйца\n2. Налить молоко\n3. Жарить',
                    value='',
                    id='recipe-steps',
                    required=True
                ),
                html.Button('Добавить', id='add-button', type='submit')
            ])
        ]),
        html.Div(id='user-recipes-panel', children=[
            dcc.Input(id='recipe-search', placeholder='Найти блюдо',
                      type='text', value=''),
            html.Div(id='user-recipes-container', children=[
            ]),
            html.Div(id='test-container')
        ])
    ])


app.layout = serve_layout


@app.callback(Output('user-recipe-placeholder', 'children'), [Input('recipe-title', 'value'),
                                                              Input(
    'recipe-image', 'value'),
    Input(
    'recipe-portions', 'value'),
    Input(
    'recipe-time', 'value'),
    Input(
    'recipe-ingredients', 'value'),
    Input(
    'recipe-steps', 'value')])
def renderPlaceholderRecipe(title, image, portions, time, ingredients, steps):

    recipe_to_add = getRecipeToAdd(
        title, image, portions, time, ingredients, steps)

    return recipe(recipe_to_add)


def getValue(val, default):
    if val is None or val == '':
        return default
    else:
        return val


def getTime(val, default):
    if val is None or val == '':
        return default
    else:
        return str(val) + ' минут'


def getPortions(val, default):
    if val is None or val == '':
        return default
    else:
        val = int(float(val))
        if val == 1:
            return str(val) + ' порция'
        elif val < 5:
            return str(val) + ' порции'
        else:
            return str(val) + ' порций'


def getLines(val):
    if val is None or val == '':
        return []
    else:
        return val.split('\n')


def getRecipeToAdd(title, image, portions, time, ingredients, steps):
    title = getValue(title, 'Название блюда')
    image = getValue(
        image, 'https://s2.eda.ru/StaticContent/DefaultRecipePhoto/no-photo.svg')
    portions = getPortions(portions, '0 порций')
    time = getTime(time, '0 минут')
    ingredients = getLines(ingredients)
    steps = getLines(steps)

    return {'title': title, 'image': image, 'portions': portions, 'time': time,
            'ingredients': ingredients, 'steps': steps, 'ingredientsAmount': ''}


@app.callback(Output('user-recipes-container', 'children'), [
    Input('add-button', 'n_clicks')], [State('recipe-title', 'value'),
                                       State(
        'recipe-image', 'value'),
    State(
        'recipe-portions', 'value'),
    State(
        'recipe-time', 'value'),
    State(
        'recipe-ingredients', 'value'),
    State(
        'recipe-steps', 'value')])
def userRecipes(n_clicks, title, image, portions, time, ingredients, steps):
    recipe_to_add = getRecipeToAdd(
        title, image, portions, time, ingredients, steps)

    if n_clicks is not None:
        recipesCol.insert_one(recipe_to_add)

    return html.Div(id='user-recipes', children=[recipe(val) for val in recipesCol.find()])


def recipe(val):
    time = ''
    if 'time' in val:
        time = val['time']

    return html.Div(className='recipe', children=[
        html.Img(src=val['image']),
        html.Div(className='recipe-text', children=[
            html.H5(children=val['title']),
            html.P(className='recipe-meta',
                   children=val['portions'] + '  ' + time),
            html.Details([
                html.Summary(
                    str(len(val['ingredients'])) + ' ингредиента(ов)'),
                html.Div(children=[
                    html.P(ingredientLine) for ingredientLine in val['ingredients']
                ])
            ]),
            html.Details([
                html.Summary(str(len(val['steps'])) + ' шаг(ов)'),
                html.Div(children=[
                    html.P(stepLine) for stepLine in val['steps']
                ])
            ])
        ]),
        html.Button('Delete', id=randomString() )
    ])


@app.callback(Output('test-container', 'children'), deleteButtons)
def deleteRecipe(*args):
    return 'text'
if __name__ == '__main__':
    app.run_server(debug=True)
