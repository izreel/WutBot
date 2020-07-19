'''
File for class of commands dealing with images (mainly classifying them)
'''
from discord.ext import commands
import cv2
import numpy as np
import tensorflow as tf
import os
import shutil
import requests


class ImageClassifier(commands.Cog):
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data
        self.classifier = tf.keras.models.load_model(data["model_weights"])

    #download an image from a given URL. Mainly used when $classify command also includes a url instead of an attachment
    def download_image(self, url):
        r = requests.get(url, stream= True)

        if r.status_code == 200:
            r.raw.decode_content = True
            with open(self.data["images"], 'wb') as f:
                shutil.copyfileobj(r.raw, f)
                f.close()
        else:
            return False
        return True


    #gets image and modifies it so that it can be fed to the model
    def get_image(self):
        image = cv2.imread(self.data["images"])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (200,200))
        image = np.expand_dims(image, axis= 0)
        return image

    '''
    Given an input of an image(s) or url of an image, use a neural network to classify them as either a dog or cat picture.
    '''
    @commands.command()
    async def classify(self, ctx):
        results = []
        
        #loops every attachment added to command call and classifies them one by one
        for attachment in  ctx.message.attachments:
            await attachment.save(self.data["images"])
            result = self.classifier.predict(self.get_image())
            results.append(result.round())

        #loops through every url given and downloads image from url and classifies them one by one
        for embed in ctx.message.embeds:
            image_url = embed.url
            
            if not self.download_image(image_url):
                await ctx.channel.send('Could not properly download image')
                return
            
            result = self.classifier.predict(self.get_image())
            results.append(result.round())
        
        if len(results) > 1:
            result_output = 'The following from top to bottom are: '
        elif len(results) == 1:
            result_output = 'This is a '
        else:
            result_output = 'Nothing to classify, try again'

        for result in results:
            if result == 1:
                result_output += 'Dog '
            else:
                result_output += 'Cat '
        
        await ctx.channel.send(result_output)
        os.remove(self.data["images"])