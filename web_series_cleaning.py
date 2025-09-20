import pandas as pd

# --- Load your dataset ---
data = pd.read_csv("webseries_with_genre.csv")

# Drop all rows where ratings are completely missing
data = data.dropna(subset=['ratings'])

# Replacing 'Not Rated' with NaN so we treat it as missing
data['ratings'] = data['ratings'].replace('Not Rated', pd.NA)

# Convert ratings column to numeric
data['ratings'] = pd.to_numeric(data['ratings'], errors='coerce')

# Fill any remaining NaN values with the mean rating
mean_rating = data['ratings'].mean()
data['ratings'] = data['ratings'].fillna(mean_rating)

# Drop all rows where director name are completely missing
data = data.dropna(subset=['director_name'])

# Drop all rows where performers are completely missing
data = data.dropna(subset=['performers'])

# droping unnecessary column
data.drop('series_link', axis=1, inplace=True)
data.drop('unnamed', axis=1, inplace=True)

# Drop all rows where performers are completely missing
data = data.dropna(subset=['ott_platform'])

null_percentage = (data.isnull().sum() / len(data)) * 100
print(null_percentage)

# Define priority order (lower number = higher priority)
priority = {
    "Mystery": 1,
    "Crime": 2,
    "Action": 3,
    "Reality": 4,
    "Documentary": 5,
    "Drama": 6,
    "Comedy": 7,
    "Animation": 8,
    "Adventure": 9,
    "Fantasy": 10,
    "Sci-Fi & Fantasy": 11,
    "Romance": 12,
    "Family": 13
}

def choose_genre(genre_str):
    if pd.isna(genre_str):
        return None
    # Normalize by replacing "&" with "," and splitting
    genres = [g.strip() for g in genre_str.replace("&", ",").split(",")]
    # Sort by priority and return the best one
    genres_sorted = sorted(genres, key=lambda g: priority.get(g, 999))
    return genres_sorted[0] if genres_sorted else None

# Apply function to create a cleaned genre column
data["genre"] = data["genre"].apply(choose_genre)

# saving the cleaned file
data.to_csv("webseries_cleaned(1).csv", index=False)

# Keep only the first genre from multiple values in the 'genre' column
data['genre'] = data['genre'].apply(lambda x: x.split()[0] if isinstance(x, str) else x)

# Save the cleaned dataset to a new CSV
data.to_csv("webseries_cleaned(1).csv", index=False)

# Count rows with NaN or 'Unknown' values in any column
rows_with_unknown = data.apply(lambda x: x.astype(str).str.lower().eq('unknown')).any(axis=1)

# Calculate percentage
percentage_unknown = (rows_with_unknown.sum() / len(data)) * 100

print(f"Percentage of rows with unknown values: {percentage_unknown:.2f}%")