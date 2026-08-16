import unittest
import pandas as pd
import json

from dashboard import build_filter_query, mongo_to_df, cached_query

class MockDB:
    def read(self, query):
        if query == {}:
            return [
                {"breed": "Labrador Retriever", "age_upon_outcome_in_weeks": 50, "sex_upon_outcome": "Intact Female"},
                {"breed": "German Shepherd", "age_upon_outcome_in_weeks": 80, "sex_upon_outcome": "Intact Male"}
            ]
        if "breed" in query:
            return [{"breed": b} for b in query["breed"]["$in"]]
        return []

# override db inside mongo_to_df
import dashboard
dashboard.db = MockDB()

class TestDashboardAlgorithms(unittest.TestCase):

    def test_build_filter_query_water(self):
        q = build_filter_query("water")
        self.assertIn("breed", q)
        self.assertIn("sex_upon_outcome", q)
        self.assertIn("age_upon_outcome_in_weeks", q)

    def test_build_filter_query_invalid(self):
        q = build_filter_query("unknown")
        self.assertEqual(q, {})

    def test_mongo_to_df_valid(self):
        df = mongo_to_df({})
        self.assertFalse(df.empty)
        self.assertIn("breed", df.columns)

    def test_mongo_to_df_invalid_query(self):
        df = mongo_to_df(None)
        self.assertTrue(df.empty)

    def test_cached_query(self):
        q = json.dumps({})
        df1 = cached_query(q)
        df2 = cached_query(q)
        self.assertTrue(df1.equals(df2))

    def test_chart_validation(self):
        from dashboard import update_chart
        result = update_chart([])
        self.assertIn("No data", result.children)

    def test_map_validation(self):
        from dashboard import update_map
        result = update_map([], [])
        self.assertIn("No rows", result.children)

if __name__ == "__main__":
    unittest.main()
