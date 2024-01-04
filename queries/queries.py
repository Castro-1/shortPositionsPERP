import requests

# GraphQL endpoint URL
graphql_endpoint = "https://api.thegraph.com/subgraphs/name/perpetual-protocol/perpetual-v2-optimism"

# Request Headers
headers = {
    "Content-Type": "application/json"
}

# Function for fetching the funding history (may be wrong, traderMarkets not well documented)
# It can't be organized in a pretty way, taking in account that there must be new updates every minute
# However here is the code to fetch it.
def fetch_funding(trader_id):
    # Query to get the fundingPayment history in the traderMarkets.
    graphql_query = '''
    {
    trader(id: "'''+trader_id+'''") {
        dayData {
        id
        tradingVolume
        tradingFee
        date
        }
    }
    }
    '''

    # Request to get the funding history data
    response = requests.post(graphql_endpoint, headers=headers, json={"query":graphql_query})

    if response.status_code == 200:
        return response.json()["data"]["trader"]["dayData"]
    else:
        # Print an error message if the request failed
        print("Error:", response.status_code)
    
# Function that fetches the trader's total funding payment
def fetch_total_fund(trader_id):
    # Query to get the trader's total funding payment
    graphql_query = '''
    {
    trader(id: "'''+trader_id+'''") {
        fundingPayment
    }
    }
    '''

    # Request to get the funding payment data
    response = requests.post(graphql_endpoint, headers=headers, json={"query":graphql_query})

    if response.status_code == 200:
        return response.json()["data"]["trader"]["fundingPayment"]
    else:
        # Print an error message if the request failed
        print("Error:", response.status_code)

# Fetch the changed positions
def fetch_positions():
    # Query for the position changes of vPERP
    graphql_query = """
    {
        positionChangeds(
            where: {baseToken: "0x9482AaFdCed6b899626f465e1FA0Cf1B1418d797"}
            orderBy: blockNumberLogIndex
            orderDirection: desc
        ) {
            id
            trader
            exchangedPositionSize
            exchangedPositionNotional
            openNotional
            positionSizeAfter
            swappedPrice
        }
    }
    """

    # Request to get the vPERP position changes
    response = requests.post(graphql_endpoint, headers=headers, json={"query":graphql_query})

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["data"]["positionChangeds"]
    else:
        # Print an error message if the request failed
        print("Error:", response.status_code)