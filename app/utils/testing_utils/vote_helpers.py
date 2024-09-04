from utils.testing_utils.generic_helpers import GenericTestCasesHelpers


class VoteTestCasesHelpers(GenericTestCasesHelpers):
    def create_vote(self, username, token, data):
        url = "/api/votes/v1/create"

        return self.send_request(
            username, token, url, data=data, format="json", method="post"
        )

    def filter_votes(self, username, token, param_dict=None):
        if param_dict is None or len(param_dict.keys()) < 1:
            fetch_user_url = "/api/votes/v1/filter?items_per_page=10&page=1"
        else:
            filter_tring = self.generate_filter_string(param_dict)
            fetch_user_url = f"/api/votes/v1/filter{filter_tring}"

        return self.send_request(username, token, fetch_user_url, method="get")

    def get_vote(self, username, token, id):
        url = f"/api/votes/v1/{id}"

        return self.send_request(username, token, url, method="get")

    def delete_vote(self, username, token, id):
        url = f"/api/votes/v1/{id}"

        return self.send_request(username, token, url, method="delete")
