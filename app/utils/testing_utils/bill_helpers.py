from utils.testing_utils.generic_helpers import GenericTestCasesHelpers


class BillTestCasesHelpers(GenericTestCasesHelpers):
    def create_bill(self, username, token, data):
        url = "/api/bills/v1/create"
        return self.send_request(
            username, token, url, data=data, format="json", method="post"
        )

    def filter_bills(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/bills/v1/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/bills/v1/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_bill(self, username, token, id):
        url = f"/api/bills/v1/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_bill(self, username, token, id):
        url = f"/api/bills/v1/{id}"

        return self.send_request(username, token, url, method="delete")
