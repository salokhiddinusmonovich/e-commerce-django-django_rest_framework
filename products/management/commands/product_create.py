import os
import json

import pandas as pd
from django.core.files import File
from django.core.management.base import BaseCommand
from products.models import Product, Category, Images

class Command(BaseCommand):
    help = "Closes the specified poll for voting"
    DATA_PATH = "/home/user/PycharmProjects/Ecommerce/data/"

    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str)

    def handle(self, *args, **options):
        file_name = options.get('file_name')
        df = pd.read_csv(f"{self.DATA_PATH}{file_name}", sep="|")
        print(df.columns)
        for index, row in df.iterrows():
            print(row['title'])
            category, created = Category.objects.get_or_create(name=row['category'])

            try:
                detail = json.loads(row['detail'])
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f"Error decoding JSON in 'detail' field: {e}"))
                continue

            product = Product.objects.create(
                category=category,
                title=row['title'],
                description=row['description'],
                price=row['price'],
                quantity=row['quantity'],
                detail=detail,
            )
            for image_path in row['images'].split():
                with open(image_path, 'rb') as img_file:
                    instance = Images.objects.create(product=product)
                    instance.image.save(os.path.basename(image_path), File(img_file), save=True)
                    instance.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created product: {product.title}')
            )
