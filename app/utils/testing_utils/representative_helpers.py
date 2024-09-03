from utils.testing_utils.generic_helpers import GenericTestCasesHelpers


class RepresentativeTestCasesHelpers(GenericTestCasesHelpers):
    def create_representative(self, username, token, data=None):
        url = "/api/representatives/v1/create"

        if data is None:
            data = {
                "area_represented": "Test Area",
                "full_name": "Mark Mende",
                "house": "NATIONAL",
                "position": "MP",
                "position_type": "ELECTED",
                "gender": "M",
            }
        return self.send_request(
            username, token, url, data=data, format="json", method="post"
        )

    def filter_representatives(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/representatives/v1/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/representatives/v1/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_representative(self, username, token, id):
        url = f"/api/representatives/v1/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_representative(self, username, token, id):
        url = f"/api/representatives/v1/{id}"

        return self.send_request(username, token, url, method="delete")
