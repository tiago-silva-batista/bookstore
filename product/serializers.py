from rest_framework import serializers
from .models.category import Category
from .models.product import Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]


class ProductSerializer(serializers.ModelSerializer):
    # leitura (read): categorias aninhadas
    category = CategorySerializer(many=True, read_only=True)
    # escrita (write): lista de IDs de categoria
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), write_only=True, required=False
    )

    # validações de campo
    title = serializers.CharField(min_length=3)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = Product
        fields = ["id", "title", "description", "price", "category", "category_ids"]

    def validate_title(self, value: str) -> str:
        qs = Product.objects.filter(title__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe produto com esse título.")
        return value

    def create(self, validated_data):
        cat_ids = validated_data.pop("category_ids", [])
        product = Product.objects.create(**validated_data)
        if cat_ids:
            product.category.set(cat_ids)
        return product

    def update(self, instance, validated_data):
        cat_ids = validated_data.pop("category_ids", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if cat_ids is not None:
            instance.category.set(cat_ids)
        return instance
