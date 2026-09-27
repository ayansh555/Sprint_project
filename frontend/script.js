const API_URL = "http://127.0.0.1:8000";

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const resultsContainer = document.getElementById("results");
const searchStatus = document.getElementById("searchStatus");

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

let currentResults = [];


/* =========================================================
   SEARCH
========================================================= */

async function searchProducts(query) {

    query = query.trim();

    if (!query) {

        searchStatus.textContent =
            "Please enter something to search.";

        searchInput.focus();

        return;
    }


    searchStatus.textContent =
        "✦ Understanding your request...";


    resultsContainer.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            Finding products that match your intent...
        </div>
    `;


    interpretationSection.classList.add(
        "hidden"
    );


    try {

        const response =
            await fetch(
                `${API_URL}/search/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
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


        searchStatus.textContent =
            "";
        

        document
            .getElementById(
                "search-results-section"
            )
            ?.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


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
                    Make sure FastAPI is running on
                    port 8000.
                </p>

                <small>
                    ${escapeHtml(
                        error.message
                    )}
                </small>

            </div>
        `;
    }
}


/* =========================================================
   DISPLAY PRODUCTS
========================================================= */

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
                    Try describing what you need
                    in a different way.
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


/* =========================================================
   PRODUCT CARD
========================================================= */

function createProductCard(
    product,
    index
) {

    const image =
        createProductImage(product);


    const price =
        formatPrice(product);


    const rating =
        product.rating !== null &&
        product.rating !== undefined
            ? `⭐ ${Number(
                product.rating
            ).toFixed(1)}`
            : "No rating";


    const similarity =
        product.similarity_score !== undefined &&
        product.similarity_score !== null
            ? `
                <span class="match-badge">
                    AI MATCH
                    ${Math.round(
                        Number(
                            product.similarity_score
                        ) * 100
                    )}%
                </span>
            `
            : "";


    return `

        <article
            class="product-card"
            data-index="${index}"
        >

            <div class="product-visual">

                ${image}

                <button
                    class="wishlist"
                    type="button"
                    title="Add to wishlist"
                >
                    ♡
                </button>

            </div>


            <div class="product-info">

                <div class="product-category">

                    ${escapeHtml(
                        product.category ||
                        "Product"
                    )}

                </div>


                <div class="product-name">

                    ${createProductName(
                        product
                    )}

                </div>


                <div class="product-brand">

                    ${escapeHtml(
                        product.brand ||
                        "Unknown brand"
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


                <div class="product-actions">

                    <button
                        class="view-product"
                        data-index="${index}"
                        type="button"
                    >
                        View Product
                    </button>


                    ${createPrimaryBuyButton(
                        product
                    )}

                </div>

            </div>

        </article>
    `;
}


/* =========================================================
   IMAGE
========================================================= */

function createProductImage(product) {

    if (!product.image_url) {

        return `
            <div class="product-image-placeholder">

                <span>
                    ${getProductEmoji(
                        product.category
                    )}
                </span>

                <small>
                    Image unavailable
                </small>

            </div>
        `;
    }


    const image = `

        <img
            src="${escapeAttribute(
                product.image_url
            )}"
            alt="${escapeAttribute(
                product.product_name ||
                "Product"
            )}"
            class="product-real-image"
            loading="lazy"
            onerror="handleImageError(this)"
        >
    `;


    const url =
        getMainProductURL(product);


    if (!url) {

        return image;
    }


    return `

        <a
            href="${escapeAttribute(url)}"
            target="_blank"
            rel="noopener noreferrer"
            class="product-image-link"
        >

            ${image}

        </a>
    `;
}


/* =========================================================
   PRODUCT NAME
========================================================= */

function createProductName(product) {

    const name =
        product.product_name ||
        "Unnamed Product";


    const url =
        getMainProductURL(product);


    if (!url) {

        return escapeHtml(name);
    }


    return `
        <a
            href="${escapeAttribute(url)}"
            target="_blank"
            rel="noopener noreferrer"
            class="product-name-link"
        >
            ${escapeHtml(name)}
        </a>
    `;
}


/* =========================================================
   IMAGE ERROR
========================================================= */

function handleImageError(image) {

    image.style.display =
        "none";


    const parent =
        image.parentElement;


    if (!parent) return;


    parent.innerHTML = `

        <div class="product-image-placeholder">

            <span>
                🛍️
            </span>

            <small>
                Image unavailable
            </small>

        </div>
    `;
}


/* =========================================================
   URL
========================================================= */

function getMainProductURL(product) {

    return (
        product.product_url ||
        product.amazon_url ||
        product.flipkart_url ||
        product.croma_url ||
        product.reliance_url ||
        product.official_url ||
        null
    );
}


/* =========================================================
   BUY BUTTON
========================================================= */

function createPrimaryBuyButton(product) {

    if (product.amazon_url) {

        return `
            <a
                href="${escapeAttribute(
                    product.amazon_url
                )}"
                target="_blank"
                rel="noopener noreferrer"
                class="buy-button"
            >
                Amazon →
            </a>
        `;
    }


    if (product.product_url) {

        return `
            <a
                href="${escapeAttribute(
                    product.product_url
                )}"
                target="_blank"
                rel="noopener noreferrer"
                class="buy-button"
            >
                Buy →
            </a>
        `;
    }


    return "";
}


/* =========================================================
   PRODUCT EVENTS
========================================================= */

function attachProductEvents() {

    document
        .querySelectorAll(
            ".view-product"
        )
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
        .querySelectorAll(
            ".wishlist"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                event => {

                    event.stopPropagation();


                    button.classList.toggle(
                        "active"
                    );


                    button.textContent =
                        button.classList.contains(
                            "active"
                        )
                            ? "♥"
                            : "♡";
                }
            );
        });
}


/* =========================================================
   MODAL
========================================================= */

function openProductModal(product) {

    if (!product) return;


    const price =
        formatPrice(product);


    const rating =
        product.rating !== null &&
        product.rating !== undefined
            ? `⭐ ${Number(
                product.rating
            ).toFixed(1)}`
            : "No rating";


    const image =
        product.image_url

            ? `
                <img
                    src="${escapeAttribute(
                        product.image_url
                    )}"
                    alt="${escapeAttribute(
                        product.product_name
                    )}"
                    class="modal-product-image"
                >
            `

            : `
                <div class="modal-image-placeholder">

                    <span>
                        ${getProductEmoji(
                            product.category
                        )}
                    </span>

                    <small>
                        Image unavailable
                    </small>

                </div>
            `;


    modalBody.innerHTML = `

        <div class="modal-product">

            <div class="modal-product-image-container">

                ${image}

            </div>


            <div class="modal-product-details">

                <div class="modal-category">

                    ${escapeHtml(
                        product.category ||
                        "Product"
                    )}

                </div>


                <h2>

                    ${escapeHtml(
                        product.product_name ||
                        "Product"
                    )}

                </h2>


                <p class="modal-brand">

                    ${escapeHtml(
                        product.brand ||
                        "Unknown brand"
                    )}

                </p>


                <div class="modal-price-rating">

                    <strong>
                        ${price}
                    </strong>

                    <span>
                        ${rating}
                    </span>

                </div>


                <p class="modal-description">

                    ${escapeHtml(
                        product.description ||
                        "No description available."
                    )}

                </p>


                <div class="modal-retailers">

                    <h3>
                        Available from
                    </h3>

                    <div class="retailer-buttons">

                        ${createRetailerButtons(
                            product
                        )}

                    </div>

                </div>


                <button
                    class="modal-close-button"
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


/* =========================================================
   RETAILERS
========================================================= */

function createRetailerButtons(product) {

    const buttons = [];


    const retailers = [
        [
            "amazon_url",
            "Amazon →"
        ],
        [
            "flipkart_url",
            "Flipkart →"
        ],
        [
            "croma_url",
            "Croma →"
        ],
        [
            "reliance_url",
            "Reliance →"
        ],
        [
            "official_url",
            "Official Website →"
        ]
    ];


    retailers.forEach(
        ([key, label]) => {

            if (product[key]) {

                buttons.push(`

                    <a
                        href="${escapeAttribute(
                            product[key]
                        )}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="retailer-button"
                    >
                        ${label}
                    </a>

                `);
            }
        }
    );


    if (!buttons.length) {

        return `
            <span class="no-retailer">
                No verified purchase link available.
            </span>
        `;
    }


    return buttons.join("");
}


/* =========================================================
   PRICE
========================================================= */

function formatPrice(product) {

    if (
        product.price === null ||
        product.price === undefined ||
        Number(product.price) <= 0
    ) {

        return "Price unavailable";
    }


    const price =
        Number(product.price);


    if (
        product.amazon_url ||
        String(product.product_id || "")
            .startsWith("B")
    ) {

        return `$${price.toLocaleString(
            "en-US",
            {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }
        )}`;
    }


    return `₹${price.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    )}`;
}


/* =========================================================
   RECOMMENDATIONS
========================================================= */

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
        "Finding products for you...";


    recommendationsContainer.innerHTML = `

        <div class="loading">

            <div class="spinner"></div>

            Creating personalized recommendations...

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


        if (!products.length) {

            recommendationsContainer.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        ♡
                    </div>

                    <h3>
                        No recommendations found
                    </h3>

                    <p>
                        Try another User ID.
                    </p>

                </div>
            `;

            return;
        }


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
            `${products.length} products recommended for ${userId}`;

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
                    ${escapeHtml(
                        error.message
                    )}
                </small>

            </div>
        `;
    }
}


/* =========================================================
   RECOMMENDATION CARD
========================================================= */

function createRecommendationCard(
    product,
    index
) {

    return createProductCard(
        product,
        index
    );
}


/* =========================================================
   SUGGESTIONS
========================================================= */

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

                searchProducts(query);
            }
        );
    });


/* =========================================================
   CATEGORIES
========================================================= */

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

                searchProducts(query);
            }
        );
    });


/* =========================================================
   SEARCH BUTTON
========================================================= */

searchButton.addEventListener(
    "click",
    () =>
        searchProducts(
            searchInput.value
        )
);


searchInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            event.preventDefault();

            searchProducts(
                searchInput.value
            );
        }
    }
);


/* =========================================================
   RECOMMENDATION
========================================================= */

recommendationButton.addEventListener(
    "click",
    getRecommendations
);


userIdInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            event.preventDefault();

            getRecommendations();
        }
    }
);


/* =========================================================
   SORT
========================================================= */

sortSelect.addEventListener(
    "change",
    () => {

        const sorted =
            [...currentResults];


        switch (
            sortSelect.value
        ) {

            case "rating":

                sorted.sort(
                    (a, b) =>
                        (b.rating || 0) -
                        (a.rating || 0)
                );

                break;


            case "price-low":

                sorted.sort(
                    (a, b) =>
                        (a.price || 0) -
                        (b.price || 0)
                );

                break;


            case "price-high":

                sorted.sort(
                    (a, b) =>
                        (b.price || 0) -
                        (a.price || 0)
                );

                break;
        }


        displayProducts(
            sorted
        );
    }
);


/* =========================================================
   FILTER
========================================================= */

document
    .querySelectorAll(".filter")
    .forEach(filter => {

        filter.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(
                        ".filter"
                    )
                    .forEach(
                        item =>
                            item.classList.remove(
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


                let filtered =
                    [...currentResults];


                if (type === "budget") {

                    filtered =
                        filtered.filter(
                            product =>
                                Number(
                                    product.price
                                ) <= 5000
                        );
                }


                if (type === "rating") {

                    filtered =
                        filtered.filter(
                            product =>
                                Number(
                                    product.rating
                                ) >= 4
                        );
                }


                displayProducts(
                    filtered
                );
            }
        );
    });


/* =========================================================
   MODAL CLOSE
========================================================= */

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


document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape" &&
            !productModal.classList.contains(
                "hidden"
            )
        ) {

            closeProductModal();
        }
    }
);


/* =========================================================
   EMOJI
========================================================= */

function getProductEmoji(category) {

    const value =
        String(category || "")
            .toLowerCase();


    if (
        value.includes("laptop") ||
        value.includes("computer")
    )
        return "💻";


    if (
        value.includes("phone") ||
        value.includes("mobile")
    )
        return "📱";


    if (
        value.includes("headphone") ||
        value.includes("audio") ||
        value.includes("earbud")
    )
        return "🎧";


    if (
        value.includes("shoe") ||
        value.includes("footwear")
    )
        return "👟";


    if (value.includes("watch"))
        return "⌚";


    if (value.includes("camera"))
        return "📷";


    return "🛍️";
}


/* =========================================================
   ESCAPE
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    )
        return "";


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


function escapeAttribute(value) {

    return escapeHtml(value);
}


console.log(
    "✦ AI Shop — Premium frontend loaded"
);