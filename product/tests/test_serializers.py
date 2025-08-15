from decimal import Decimal
from django.test import TestCase
from product.models.category import Category
from product.models.product import Product
from product.serializers.product_serializer import ProductSerializer
from product.serializers.category_serializer import CategorySerializer

class TestCategorySerializer(TestCase):
    def test_ok(self):
        cat = Category.objects.create(title="Romance")
        data = CategorySerializer(cat).data
        assert "id" in data
        assert data["title"] == "Romance"

class TestProductSerializer(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(title="Tech")
        self.cat2 = Category.objects.create(title="Fiction")

    def test_create_success(self):
        payload = {
            "title": "Clean Architecture",
            "description": "Uncle Bob vibes",
            "price": "99.90",
            "category_ids": [self.cat1.id, self.cat2.id],
        }
        ser = ProductSerializer(data=payload)
        assert ser.is_valid(), ser.errors
        prod = ser.save()
        assert prod.title == "Clean Architecture"
        assert prod.price == Decimal("99.90")
        assert prod.category.count() == 2

    def test_title_min_length(self):
        ser = ProductSerializer(data={"title": "ab", "price": "10.00"})
        assert not ser.is_valid()
        assert "title" in ser.errors

    def test_price_non_negative(self):
        ser = ProductSerializer(data={"title": "Teclado", "price": "-1"})
        assert not ser.is_valid()
        assert "price" in ser.errors

    def test_title_unique_case_insensitive(self):
        Product.objects.create(title="Mouse Gamer", price=100)
        ser = ProductSerializer(data={"title": "mouse gamer", "price": "50.00"})
        assert not ser.is_valid()
        assert "title" in ser.errors

    def test_read_nested_categories(self):
        prod = Product.objects.create(title="Kindle", price=399)
        prod.category.set([self.cat1, self.cat2])
        data = ProductSerializer(prod).data
        assert len(data["category"]) == 2
        titles = sorted(c["title"] for c in data["category"])
        assert titles == ["Fiction", "Tech"]
