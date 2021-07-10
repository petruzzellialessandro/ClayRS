from unittest import TestCase, mock
import os

from orange_cb_recsys.content_analyzer.content_representation.content import FeaturesBagField
from orange_cb_recsys.content_analyzer.field_content_production_techniques.entity_linking import BabelPyEntityLinking, \
    BabelfyClient
from orange_cb_recsys.content_analyzer.raw_information_source import JSONFile

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(THIS_DIR, "../../../datasets/movies_info_reduced.json")


class TestBabelPyEntityLinking(TestCase):

    @mock.patch('orange_cb_recsys.content_analyzer.field_content_production_techniques.'
                'entity_linking.BabelfyClient')
    def test_produce_content(self, mocked):
        instance = mocked.return_value
        instance.entities = [{'babelSynsetID': 123, 'globalScore': 0.0}]

        technique = BabelPyEntityLinking()

        features_bag_list = technique.produce_content("Title", [], JSONFile(file_path))

        self.assertEqual(len(features_bag_list), 20)
        self.assertIsInstance(features_bag_list[0], FeaturesBagField)
