from rest_framework import serializers
from product.models.product import Product
from product.models.category import Category
from product.serializers.category_serializer import CategorySerializer

class ProductSerializer(serializers.ModelSerializer):
    # ↓ adiciona min_length pra passar no test_title_min_length
    title = serializers.CharField(min_length=3)

    category = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), write_only=True, required=False
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'active', 'category', 'category_ids']

    # ↓ validação pra passar no test_title_unique_case_insensitive
    def validate_title(self, value):
        qs = Product.objects.filter(title__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe produto com esse título.")
        return value

    def create(self, validated_data):
        cat_ids = validated_data.pop('category_ids', [])
        obj = Product.objects.create(**validated_data)
        if cat_ids:
            obj.category.set(cat_ids)
        return obj

    def update(self, instance, validated_data):
        cat_ids = validated_data.pop('category_ids', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if cat_ids is not None:
            instance.category.set(cat_ids)
        return instance
