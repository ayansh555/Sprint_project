const API_URL = "http://127.0.0.1:8000";


// =========================================================
// ELEMENTS
// =========================================================

const searchInput =
    document.getElementById("searchInput");

const searchButton =
    document.getElementById("searchButton");

const resultsContainer =
    document.getElementById("results");

const searchStatus =
    document.getElementById("searchStatus");

const interpretationSection =
    document.getElementById("interpretationSection");

const interpretation =
    document.getElementById("interpretation");

const resultCount =
    document.getElementById("resultCount");

const userIdInput =
    document.getElementById("userId");

const recommendationButton =
    document.getElementById("recommendationButton");

const recommendationsContainer =
    document.getElementById("recommendations");

const recommendationStatus =
    document.getElementById("recommendationStatus");

const sortSelect =
    document.getElementById("sortSelect");

const productModal =
    document.getElementById("productModal");

const modalBody =
    document.getElementById("modalBody");

const closeModal =
    document.getElementById("closeModal");

const modalOverlay =
    document.getElementById("modalOverlay");


// =========================================================
// GLOBAL DATA
// =========================================================

let currentResults = [];


// =========================================================
// SEARCH
// =========================================================

async function searchProducts(query) {

    query = query.trim();

    if (!query) {
        searchInput.focus();
        return;
    }


    searchStatus.textContent =
        "✦ AI is understanding your request...";


    resultsContainer.innerHTML = `
        <div class="loading">

            <div class="spinner"></div>

            Finding products that match your intent...

        </div>
    `;


    interpretationSection.classList.add("hidden");

    resultCount.textContent = "";


    try {

        const response = await fetch(
            `${API_URL}/search/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    query: query,
                    top_k: 8
                })
            }
        );


        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "Search response:",
            data
        );


        // AI interpretation

        if (data.interpreted_query) {

            interpretation.textContent =
                data.interpreted_query;

            interpretationSection.classList.remove(
                "hidden"
            );
        }


        currentResults =
            data.results || [];


        displayProducts(
            currentResults
        );


        searchStatus.textContent = "";


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        searchStatus.textContent =
            "Unable to connect to the AI backend.";


        resultsContainer.innerHTML = `

            <div class="error-message">

                <h3>
                    Something went wrong
                </h3>

                <p>
                    Make sure FastAPI is running on port 8000.
                </p>

                <small>
                    ${escapeHtml(error.message)}
                </small>

            </div>
        `;
    }
}


// =========================================================
// DISPLAY PRODUCTS
// =========================================================

function displayProducts(products) {

    if (!products.length) {

        resultCount.textContent =
            "0 products";


        resultsContainer.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    ✦
                </div>

                <h3>
                    No products found
                </h3>

                <p>
                    Try describing what you are looking for differently.
                </p>

            </div>
        `;

        return;
    }


    resultCount.textContent =
        `${products.length} products`;


    resultsContainer.innerHTML =
        products
            .map(
                (product, index) =>
                    createProductCard(
                        product,
                        index
                    )
            )
            .join("");


    attachProductEvents();
}


// =========================================================
// PRODUCT CARD
// =========================================================

function createProductCard(
    product,
    index
) {

    const category =
        product.category ||
        "Product";


    const emoji =
        getProductEmoji(category);


    const price =
        product.price !== null &&
        product.price !== undefined
            ? `₹${Number(
                product.price
            ).toLocaleString("en-IN")}`
            : "Price unavailable";


    const rating =
        product.rating !== null &&
        product.rating !== undefined
            ? `⭐ ${Number(
                product.rating
            ).toFixed(1)}`
            : "No rating";


    let similarity = "";


    if (
        product.similarity_score !==
            undefined &&
        product.similarity_score !== null
    ) {

        similarity = `

            <span class="match-badge">

                Semantic match:
                ${Number(
                    product.similarity_score
                ).toFixed(3)}

            </span>
        `;
    }


    return `

        <article
            class="product-card"
            data-index="${index}"
        >

            <div class="product-visual">

                <div class="product-emoji">
                    ${emoji}
                </div>

                <button
                    class="wishlist"
                    title="Add to wishlist"
                >
                    ♡
                </button>

            </div>


            <div class="product-info">

                <div class="product-category">
                    ${escapeHtml(category)}
                </div>


                <div class="product-name">

                    ${escapeHtml(
                        product.product_name ||
                        "Unnamed Product"
                    )}

                </div>


                <div class="product-brand">

                    ${escapeHtml(
                        product.brand ||
                        "Unknown Brand"
                    )}

                </div>


                <div class="product-bottom">

                    <span class="product-price">
                        ${price}
                    </span>

                    <span class="product-rating">
                        ${rating}
                    </span>

                </div>


                ${similarity}


                <button
                    class="view-product"
                    data-index="${index}"
                >
                    View Product →
                </button>

            </div>

        </article>
    `;
}


// =========================================================
// PRODUCT EVENTS
// =========================================================

function attachProductEvents() {

    document
        .querySelectorAll(".view-product")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const index =
                        Number(
                            button.dataset.index
                        );

                    openProductModal(
                        currentResults[index]
                    );
                }
            );
        });


    document
        .querySelectorAll(".wishlist")
        .forEach(button => {

            button.addEventListener(
                "click",
                event => {

                    event.stopPropagation();

                    button.textContent =
                        button.textContent === "♡"
                            ? "♥"
                            : "♡";
                }
            );
        });
}


// =========================================================
// PRODUCT MODAL
// =========================================================

function openProductModal(product) {

    if (!product) {
        return;
    }


    const category =
        product.category ||
        "Product";


    const emoji =
        getProductEmoji(category);


    const price =
        product.price !== null &&
        product.price !== undefined
            ? `₹${Number(
                product.price
            ).toLocaleString("en-IN")}`
            : "Price unavailable";


    const rating =
        product.rating !== null &&
        product.rating !== undefined
            ? `⭐ ${Number(
                product.rating
            ).toFixed(1)}`
            : "No rating";


    modalBody.innerHTML = `

        <div
            style="
                display:grid;
                grid-template-columns:180px 1fr;
                gap:30px;
                align-items:center;
            "
        >

            <div
                style="
                    height:180px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border-radius:18px;
                    background:
                        radial-gradient(
                            circle,
                            rgba(110,80,255,.18),
                            transparent 70%
                        );
                    font-size:75px;
                "
            >
                ${emoji}
            </div>


            <div>

                <div
                    style="
                        color:#a28cff;
                        font-size:10px;
                        font-weight:800;
                        letter-spacing:1.5px;
                        text-transform:uppercase;
                    "
                >
                    ${escapeHtml(category)}
                </div>


                <h2
                    style="
                        margin-top:8px;
                        font-size:26px;
                    "
                >
                    ${escapeHtml(
                        product.product_name ||
                        "Product"
                    )}
                </h2>


                <p
                    style="
                        color:#7f879b;
                        margin-top:7px;
                    "
                >
                    ${escapeHtml(
                        product.brand ||
                        "Unknown Brand"
                    )}
                </p>


                <div
                    style="
                        display:flex;
                        gap:20px;
                        margin-top:20px;
                    "
                >

                    <strong
                        style="
                            font-size:22px;
                        "
                    >
                        ${price}
                    </strong>

                    <span
                        style="
                            color:#ffc95c;
                            padding-top:5px;
                        "
                    >
                        ${rating}
                    </span>

                </div>


                <button
                    style="
                        margin-top:25px;
                        padding:12px 20px;
                        border:none;
                        border-radius:10px;
                        background:linear-gradient(
                            135deg,
                            #8060ff,
                            #6544e8
                        );
                        color:white;
                        font-weight:700;
                        cursor:pointer;
                    "
                    onclick="closeProductModal()"
                >
                    Close
                </button>

            </div>

        </div>
    `;


    productModal.classList.remove(
        "hidden"
    );
}


function closeProductModal() {

    productModal.classList.add(
        "hidden"
    );
}


closeModal.addEventListener(
    "click",
    closeProductModal
);


modalOverlay.addEventListener(
    "click",
    closeProductModal
);


// =========================================================
// RECOMMENDATIONS
// =========================================================

async function getRecommendations() {

    const userId =
        userIdInput.value.trim();


    if (!userId) {

        recommendationStatus.textContent =
            "Please enter a User ID.";

        userIdInput.focus();

        return;
    }


    recommendationStatus.textContent =
        "✦ Creating personalized recommendations...";


    recommendationsContainer.innerHTML = `

        <div class="loading">

            <div class="spinner"></div>

            Finding products for you...

        </div>
    `;


    try {

        const response =
            await fetch(
                `${API_URL}/recommendations/${encodeURIComponent(
                    userId
                )}`
            );


        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );
        }


        const data =
            await response.json();


        const products =
            data.recommendations || [];


        recommendationsContainer.innerHTML =
            products
                .map(
                    (product, index) =>
                        createRecommendationCard(
                            product,
                            index
                        )
                )
                .join("");


        recommendationStatus.textContent =
            products.length
                ? `${products.length} recommendations found for ${userId}`
                : `No recommendations found for ${userId}`;


    } catch (error) {

        console.error(
            "Recommendation error:",
            error
        );


        recommendationStatus.textContent =
            "Unable to load recommendations.";


        recommendationsContainer.innerHTML = `

            <div class="error-message">

                Something went wrong.

                <br><br>

                <small>
                    ${escapeHtml(error.message)}
                </small>

            </div>
        `;
    }
}


// =========================================================
// RECOMMENDATION CARD
// =========================================================

function createRecommendationCard(
    product,
    index
) {

    const category =
        product.category ||
        "Product";


    const price =
        product.price !== null &&
        product.price !== undefined
            ? `₹${Number(
                product.price
            ).toLocaleString("en-IN")}`
            : "Price unavailable";


    const rating =
        product.rating !== null &&
        product.rating !== undefined
            ? `⭐ ${Number(
                product.rating
            ).toFixed(1)}`
            : "No rating";


    return `

        <article class="product-card">

            <div class="product-visual">

                <div class="product-emoji">
                    ${getProductEmoji(category)}
                </div>

            </div>


            <div class="product-info">

                <div class="product-category">
                    ${escapeHtml(category)}
                </div>


                <div class="product-name">

                    ${escapeHtml(
                        product.product_name ||
                        "Unnamed Product"
                    )}

                </div>


                <div class="product-brand">

                    ${escapeHtml(
                        product.brand ||
                        "Unknown Brand"
                    )}

                </div>


                <div class="product-bottom">

                    <span class="product-price">
                        ${price}
                    </span>

                    <span class="product-rating">
                        ${rating}
                    </span>

                </div>


                <span class="match-badge">
                    ♡ Recommended for you
                </span>

            </div>

        </article>
    `;
}


// =========================================================
// SUGGESTIONS
// =========================================================

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const query =
                    button.dataset.query;

                searchInput.value =
                    query;

                searchProducts(
                    query
                );

                window.scrollTo({
                    top:
                        document.getElementById(
                            "results"
                        ).offsetTop - 120,

                    behavior: "smooth"
                });
            }
        );
    });


// =========================================================
// CATEGORY BUTTONS
// =========================================================

document
    .querySelectorAll(".category-card")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const query =
                    button.dataset.query;

                searchInput.value =
                    query;

                searchProducts(
                    query
                );

                window.scrollTo({
                    top:
                        document.getElementById(
                            "results"
                        ).offsetTop - 120,

                    behavior: "smooth"
                });
            }
        );
    });


// =========================================================
// SEARCH BUTTON
// =========================================================

searchButton.addEventListener(
    "click",
    () => {

        searchProducts(
            searchInput.value
        );
    }
);


// =========================================================
// ENTER SEARCH
// =========================================================

searchInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            searchProducts(
                searchInput.value
            );
        }
    }
);


// =========================================================
// RECOMMENDATION BUTTON
// =========================================================

recommendationButton.addEventListener(
    "click",
    getRecommendations
);


// =========================================================
// ENTER USER ID
// =========================================================

userIdInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            getRecommendations();
        }
    }
);


// =========================================================
// SORT
// =========================================================

sortSelect.addEventListener(
    "change",
    () => {

        let sorted = [
            ...currentResults
        ];


        const value =
            sortSelect.value;


        if (value === "rating") {

            sorted.sort(
                (a, b) =>
                    (b.rating || 0) -
                    (a.rating || 0)
            );
        }


        if (value === "price-low") {

            sorted.sort(
                (a, b) =>
                    (a.price || 0) -
                    (b.price || 0)
            );
        }


        if (value === "price-high") {

            sorted.sort(
                (a, b) =>
                    (b.price || 0) -
                    (a.price || 0)
            );
        }


        displayProducts(
            sorted
        );
    }
);


// =========================================================
// FILTERS
// =========================================================

document
    .querySelectorAll(".filter")
    .forEach(filter => {

        filter.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(".filter")
                    .forEach(
                        f =>
                            f.classList.remove(
                                "active"
                            )
                    );


                filter.classList.add(
                    "active"
                );


                const type =
                    filter.dataset.filter;


                if (type === "all") {

                    displayProducts(
                        currentResults
                    );

                    return;
                }


                let filtered = [];


                if (type === "budget") {

                    filtered =
                        currentResults.filter(
                            p =>
                                Number(
                                    p.price
                                ) <= 5000
                        );
                }


                if (type === "rating") {

                    filtered =
                        currentResults.filter(
                            p =>
                                Number(
                                    p.rating
                                ) >= 4
                        );
                }


                displayProducts(
                    filtered
                );
            }
        );
    });


// =========================================================
// EMOJI HELPER
// =========================================================

function getProductEmoji(
    category
) {

    const value =
        category.toLowerCase();


    if (
        value.includes("laptop") ||
        value.includes("computer")
    ) {
        return "💻";
    }


    if (
        value.includes("phone") ||
        value.includes("mobile")
    ) {
        return "📱";
    }


    if (
        value.includes("headphone") ||
        value.includes("audio")
    ) {
        return "🎧";
    }


    if (
        value.includes("shoe") ||
        value.includes("footwear")
    ) {
        return "👟";
    }


    if (
        value.includes("watch")
    ) {
        return "⌚";
    }


    if (
        value.includes("camera")
    ) {
        return "📷";
    }


    if (
        value.includes("book")
    ) {
        return "📚";
    }


    if (
        value.includes("fashion") ||
        value.includes("clothing")
    ) {
        return "👕";
    }


    return "🛍️";
}


// =========================================================
// SECURITY
// =========================================================

function escapeHtml(value) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );
}


// =========================================================
// STARTUP
// =========================================================

console.log(
    "✦ AI Shop frontend loaded"
);

console.log(
    "Backend:",
    API_URL
);