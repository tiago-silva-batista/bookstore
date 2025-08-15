from decimal import Decimal
from django.test import TestCase
from product.models.category import Category
from product.models.product import Product
from product.serializers.product_serializer import ProductSerializer
from product.serializers.category_serializer import CategorySerializer


class CategorySerializerTests(TestCase):
    def test_category_serializer_ok(self):
        cat = Category.objects.create(title="Romance")
        data = CategorySerializer(cat).data
        self.assertIn("id", data)
        self.assertEqual(data["title"], "Romance")


class ProductSerializerTests(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(title="Tech", slug="tech")
        self.cat2 = Category.objects.create(title="Fiction", slug="fiction")

    def test_create_product_success(self):
        payload = {
            "title": "Clean Architecture",
            "description": "Uncle Bob vibes",
            "price": "99.90",
            "category_ids": [self.cat1.id, self.cat2.id],
        }
        ser = ProductSerializer(data=payload)
        self.assertTrue(ser.is_valid(), ser.errors)
        prod = ser.save()
        self.assertEqual(prod.title, "Clean Architecture")
        self.assertEqual(prod.price, Decimal("99.90"))
        self.assertEqual(prod.category.count(), 2)

    def test_title_min_length(self):
        ser = ProductSerializer(data={"title": "ab", "price": "10.00"})
        self.assertFalse(ser.is_valid())
        self.assertIn("title", ser.errors)

    def test_price_non_negative(self):
        ser = ProductSerializer(data={"title": "Teclado", "price": "-1"})
        self.assertFalse(ser.is_valid())
        self.assertIn("price", ser.errors)

    def test_title_unique_case_insensitive(self):
        Product.objects.create(title="Mouse Gamer", price=100)
        ser = ProductSerializer(data={"title": "mouse gamer", "price": "50.00"})
        self.assertFalse(ser.is_valid())
        self.assertIn("title", ser.errors)

    def test_read_nested_categories(self):
        prod = Product.objects.create(title="Kindle", price=399)
        prod.category.set([self.cat1, self.cat2])
        data = ProductSerializer(prod).data
        self.assertEqual(len(data["category"]), 2)
        titles = sorted(c["title"] for c in data["category"])
        self.assertEqual(titles, ["Fiction", "Tech"])
