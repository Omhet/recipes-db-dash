# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import requests
import pymongo
from pymongo import MongoClient

client = MongoClient(
    'mongodb://omhet:omhetdev16@ds227035.mlab.com:27035/omhet_db')
db = client['omhet_db']
recipesCol = db.recipes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

showcase_recipes = []


def fetch_showcase_recipes():
    url = 'https://recipes-search.glitch.me/showcase'
    response = requests.get(url)
    data = response.json()
    return data['recipes']


showcase_recipes = fetch_showcase_recipes()

app.layout = html.Div(className='flex', children=[
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Найти', children=[
            html.Div(className='flex', children=[
                dcc.Input(
                    placeholder='Найти блюдо...',
                    type='text',
                    value='',
                    id='recipe-search'
                ),
                html.Div(id='found-recipes-container')
            ])
        ]),
        dcc.Tab(label='Мои рецепты', children=[
            html.Div(className='flex-wide', children=[
                html.Div(id='user-recipe-placeholder', className='recipe'),
                html.Div(id='add-recipe-form', children=[
                    html.Label('Название', htmlFor='recipe-title'),
                    dcc.Input(
                        placeholder='Омлет',
                        type='text',
                        id='recipe-title'
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
                        id='recipe-portions'
                    ),
                    html.Label('Время приготовления (в минутах)',
                               htmlFor='recipe-time'),
                    dcc.Input(
                        placeholder='30',
                        type='number',
                        value='',
                        id='recipe-time'
                    ),
                    html.Label('Ингредиенты',
                               htmlFor='recipe-ingredients'),
                    dcc.Textarea(
                        placeholder='Яйца - 4 штуки\nМолоко - 1 литр',
                        value='',
                        id='recipe-ingredients'
                    ),
                    html.Label('Рецепт',
                               htmlFor='recipe-steps'),
                    dcc.Textarea(
                        placeholder='1. Разбить яйца\n2. Налить молоко\n3. Жарить',
                        value='',
                        id='recipe-steps'
                    ),
                    html.Button('Добавить', id='add-button')
                ])
            ]),
            html.Div(id='user-recipes-container', children=[

            ])
        ])
    ])
])


@app.callback(Output('found-recipes-container', 'children'), [Input('recipe-search', 'value')])
def recipes(search):
    if len(search) == 0:
        return html.Div(id='recipes', children=[recipe(val) for val in showcase_recipes])
    else:
        return []


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
                html.Summary(val['ingredientsAmount']),
                html.P('Content2')
            ])
        ])
    ])


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
                                                                  'recipe-steps', 'value'),
    Input('add-button', 'n_clicks')])
def addRecipe(title, image, portions, time, ingredients, steps, n_clicks):
    title = getValue(title, 'Название блюда')
    image = getValue(
        image, 'https://s2.eda.ru/StaticContent/DefaultRecipePhoto/no-photo.svg')
    portions = getPortions(portions, '0 порций')
    time = getTime(time, '0 минут')
    ingredients = getValue(ingredients, '')
    steps = getValue(steps, '')

    val = {'title': title, 'image': image, 'portions': portions, 'time': time,
           'ingredients': ingredients, 'steps': steps, 'ingredientsAmount': ''}
    return recipe(val)


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

@app.callback(Output('user-recipes-container', 'children'), [Input('recipe-title', 'value')])
def userRecipes(title):
    for x in recipesCol.find():
        print(x)
    return html.Div(id='user-recipes', children=[recipe(val) for val in recipesCol.find()])

if __name__ == '__main__':
    app.run_server(debug=True)
