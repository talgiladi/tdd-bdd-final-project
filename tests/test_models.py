# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_deserialize_a_product(self):
        """It should deserialize a product"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.available = True
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        data = product.serialize()
        product2 = Product()
        product2.deserialize(data)
        self.assertEqual(product2.name, product.name)
        self.assertEqual(product2.description, product.description)
        self.assertEqual(Decimal(product2.price), product.price)
        self.assertEqual(product2.available, product.available)
        self.assertEqual(product2.category, product.category)

    def test_deserialize_invalid_category(self):
        """It should raise an error for invalid category"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        data = product.serialize()
        data["category"] = 'aaa'
        product2 = Product()
        self.assertRaises(DataValidationError, product2.deserialize, data)

    def test_deserialize_missing_name(self):
        """It should raise an error for missing name"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        data = product.serialize()
        del data["name"]
        product2 = Product()
        self.assertRaises(DataValidationError, product2.deserialize, data)

    def test_deserialize_non_dictionary(self):
        """It should raise an error for non dictionary type"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product2 = Product()
        self.assertRaises(DataValidationError, product2.deserialize, 'aa')

    def test_read_a_product(self):
        """It should Read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a product"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product.description = "my new description"
        product.update()

        products = Product.all()
        self.assertEqual(len(products), 1)
        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_no_id(self):
        """It should raise an error for update with no id"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product.description = "my new description"
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_find_product_by_name(self):
        """It should find a product by name"""
        products = Product.all()
        self.assertEqual(products, [])
        for i in range(5):
            product = ProductFactory()
            product.id = None
            product.name = f"my name{i}"
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
            products.append(product)

        for _ in products:
            found_product = Product.find_by_name(product.name)[0]
            self.assertIsNotNone(found_product)
            self.assertEqual(found_product.id, product.id)
            self.assertEqual(found_product.name, product.name)

    def test_find_product_by_availability(self):
        """It should find a product by availability"""
        products = Product.all()
        available = 0
        self.assertEqual(products, [])
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
            products.append(product)
            if product.available:
                available += 1

        loaded = Product.find_by_availability(True)
        self.assertEqual((loaded.count()), available)

        loaded = Product.find_by_availability(False)
        self.assertEqual((loaded.count()), 10-available)

    def test_find_product_by_category(self):
        """It should find a product by category"""
        products = Product.all()
        self.assertEqual(products, [])
        category = ''
        number_of_products = 0
        for i in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
            products.append(product)
            if i == 0:
                category = product.category
            if product.category == category:
                number_of_products += 1
        loaded = Product.find_by_category(category)
        self.assertEqual((loaded.count()), number_of_products)
        for item in loaded:
            self.assertEqual(item.category, category)

    def test_find_product_by_price(self):
        """It should find a product by price"""
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(10):
            product = ProductFactory()
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
            products.append(product)
        product = products[1]
        loaded = Product.find_by_price(product.price)
        for item in loaded:
            self.assertEqual(item.price, product.price)

    def test_delete_a_product(self):
        """It should Delete a product"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products"""
        products = Product.all()
        self.assertEqual(products, [])
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
            # Assert that it was assigned an id and shows up in the database
            self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 5)
