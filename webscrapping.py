import bs4 as bs
import urllib.request as url
import csv


def scrape_yelp_reviews(yelp_url, start_page=0):
    source = url.urlopen(yelp_url)
    page_soup = bs.BeautifulSoup(source, "html.parser")

    # Extract restaurant details
    main = page_soup.find("div", {"class": "photo-header-content-container__09f24__jDLBB css-1qn0b6x"})

    if not main:
        print(f"No restaurant details found on the page: {yelp_url}")
        return None

    restaurant_name = main.find("h1").text
    total_review = main.find("a").text
    total_stars_rating = main.find("span", {"class": "css-1d8srnw"}).div.get('aria-label')

    print("Restaurant Name:", restaurant_name)
    print("Total Reviews:", total_review)
    print("Total Stars Rating:", total_stars_rating)

    # Extract individual reviews
    reviews = page_soup.find_all("div", {"class": "css-1qn0b6x"})

    # Create lists to store data
    reviewer_list = []
    rating_list = []
    review_text_list = []

    for review in reviews:
        try:
            reviewer = review.find("a", {"class": "css-19v1rkv"})
            rating_element = review.find("span", {"class": "css-1d8srnw"})
            review_text_element = review.find("p", {"class": "comment__09f24__D0cxf css-qgunke"})

            if reviewer and rating_element and review_text_element:
                reviewer_text = reviewer.text
                rating = rating_element.div.get('aria-label')
                review_text = review_text_element.text

                # Append data to lists
                reviewer_list.append(reviewer_text)
                rating_list.append(rating)
                review_text_list.append(review_text)

        except AttributeError as e:
            print("Error:", e)

    # Print the extracted data for verification
    for i in range(len(reviewer_list)):
        print("Reviewer:", reviewer_list[i])
        print("Rating:", rating_list[i])
        print("Review:", review_text_list[i])
        print("=" * 20)

    return {
        "restaurant_name": restaurant_name,
        "total_review": total_review,
        "total_stars_rating": total_stars_rating,
        "reviewer_list": reviewer_list,
        "rating_list": rating_list,
        "review_text_list": review_text_list
    }


def save_to_csv(filename, data_list):
    encountered_reviewers = set()
    with open(filename, mode='a', newline='', encoding='utf-8') as csv_file:  # Use 'a' for append mode
        csv_writer = csv.writer(csv_file)

        if csv_file.tell() == 0:  # Check if file is empty, write header only if needed
            csv_writer.writerow(["Restaurant Name", "Total Reviews", "Total Stars Rating", "Reviewer", "Rating", "Review Text"])

        for data in data_list:
            if not data.get("written_to_csv", False):
                # Write restaurant details only once
                csv_writer.writerow([
                    data["restaurant_name"],
                    data["total_review"],
                    data["total_stars_rating"],
                    "", "", ""
                ])
                data["written_to_csv"] = True

            # Write individual reviews for each restaurant
            for i in range(len(data["reviewer_list"])):
                current_reviewer = data["reviewer_list"][i]

                if current_reviewer not in encountered_reviewers and current_reviewer!="Suggest an edit":
                    # Write to CSV only if the reviewer is not encountered before
                    csv_writer.writerow([
                        "",
                        "",
                        "",
                        current_reviewer,
                        data["rating_list"][i],
                        data["review_text_list"][i]
                    ])
                    encountered_reviewers.add(current_reviewer)

    print(f"Data saved to {filename}")

# Example usage with the provided URL
yelp_base_url = "https://www.yelp.ca/biz/pai-northern-thai-kitchen-toronto-5?osq=Restaurants"
#webpages = 3560 total webpages are 3560 but we just took 2 for practice.
webpages = 2

# Initialize an empty list to store all the data
all_data = []

for i in range(webpages):
    start_index = i * 10
    yelp_url = f"{yelp_base_url}&start={start_index}#reviews"
    restaurant_data = scrape_yelp_reviews(yelp_url, start_page=i * 10)

    if restaurant_data:
        # Append data to the list
        all_data.append(restaurant_data)

# Save all the data to CSV after the loop
if all_data:
    save_to_csv("yelp_reviews_combined.csv", all_data)
