const API_URL = "http://127.0.0.1:8000";


/* =========================================================
   ELEMENTS
========================================================= */

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


/* =========================================================
   AUTH ELEMENTS
========================================================= */

const loginButton =
    document.getElementById("loginButton");

const registerButton =
    document.getElementById("registerButton");

const userMenu =
    document.getElementById("userMenu");

const loggedInUsername =
    document.getElementById("loggedInUsername");

const logoutButton =
    document.getElementById("logoutButton");

const authModal =
    document.getElementById("authModal");

const authModalOverlay =
    document.getElementById("authModalOverlay");

const closeAuthModal =
    document.getElementById("closeAuthModal");

const loginFormContainer =
    document.getElementById("loginFormContainer");

const registerFormContainer =
    document.getElementById("registerFormContainer");

const loginForm =
    document.getElementById("loginForm");

const registerForm =
    document.getElementById("registerForm");

const showRegisterButton =
    document.getElementById("showRegisterButton");

const showLoginButton =
    document.getElementById("showLoginButton");

const loginEmail =
    document.getElementById("loginEmail");

const loginPassword =
    document.getElementById("loginPassword");

const registerUsername =
    document.getElementById("registerUsername");

const registerEmail =
    document.getElementById("registerEmail");

const registerPassword =
    document.getElementById("registerPassword");

const loginStatus =
    document.getElementById("loginStatus");

const registerStatus =
    document.getElementById("registerStatus");


/* =========================================================
   AUTH STORAGE
========================================================= */

const AUTH_TOKEN_KEY =
    "ai_shop_access_token";

const AUTH_USER_KEY =
    "ai_shop_user";


/* =========================================================
   GLOBAL DATA
========================================================= */

let currentResults = [];


/* =========================================================
   USER INTERACTION TRACKING
========================================================= */

async function recordInteraction(
    productId,
    interactionType
) {

    const token =
        localStorage.getItem(
            AUTH_TOKEN_KEY
        );

    if (!token || !productId) {
        return;
    }

    try {

        const response =
            await fetch(
                `${API_URL}/interactions/?product_id=${encodeURIComponent(
                    productId
                )}&interaction_type=${encodeURIComponent(
                    interactionType
                )}`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        if (!response.ok) {

            console.warn(
                "Interaction tracking failed:",
                response.status
            );

            return;
        }


        const data =
            await response.json();


        console.log(
            "Interaction recorded:",
            data
        );

    } catch (error) {

        console.warn(
            "Interaction tracking error:",
            error
        );
    }
}


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
   PRODUCT URL
========================================================= */

function getMainProductURL(product) {

    return (
        product.product_url ||
        product.amazon_url ||
        product.flipkart_url ||
        product.croma_url ||
        product.myntra_url ||
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


                    const product =
                        currentResults[index];


                    if (!product) {
                        return;
                    }


                    recordInteraction(
                        product.product_id,
                        "click"
                    );


                    openProductModal(
                        product
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


                    const card =
                        button.closest(
                            ".product-card"
                        );


                    if (!card) {
                        return;
                    }


                    const index =
                        Number(
                            card.dataset.index
                        );


                    const product =
                        currentResults[index];


                    if (!product) {
                        return;
                    }


                    button.classList.toggle(
                        "active"
                    );


                    const isActive =
                        button.classList.contains(
                            "active"
                        );


                    button.textContent =
                        isActive
                            ? "♥"
                            : "♡";


                    if (isActive) {

                        recordInteraction(
                            product.product_id,
                            "wishlist"
                        );
                    }
                }
            );
        });
}


/* =========================================================
   PRODUCT MODAL
========================================================= */

function openProductModal(product) {

    if (!product) return;


    recordInteraction(
        product.product_id,
        "view"
    );


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
                    type="button"
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
            "myntra_url",
            "Myntra →"
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

    const token =
        localStorage.getItem(
            AUTH_TOKEN_KEY
        );


    const user =
        JSON.parse(
            localStorage.getItem(
                AUTH_USER_KEY
            ) || "null"
        );


    if (!token || !user) {

        recommendationStatus.textContent =
            "Please login to see personalized recommendations.";


        recommendationsContainer.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    🔐
                </div>

                <h3>
                    Login required
                </h3>

                <p>
                    Login to get personalized product recommendations.
                </p>

            </div>
        `;

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
                `${API_URL}/recommendations/?limit=10`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch (jsonError) {

            console.warn(
                "Recommendation response was not JSON.",
                jsonError
            );
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Recommendation request failed (${response.status})`
            );
        }


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
                        Interact with some products and we'll
                        personalize your recommendations.
                    </p>

                </div>
            `;

            recommendationStatus.textContent =
                "No personalized recommendations yet.";

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


        attachRecommendationEvents(
            products
        );


        recommendationStatus.textContent =
            `${products.length} personalized products for ${user.username}`;


    } catch (error) {

        console.error(
            "Recommendation error:",
            error
        );


        recommendationStatus.textContent =
            "Unable to load recommendations.";


        recommendationsContainer.innerHTML = `

            <div class="error-message">

                <h3>
                    Something went wrong
                </h3>

                <br>

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

    return `
        <article
            class="product-card recommendation-card"
            data-recommendation-index="${index}"
        >

            <div class="product-visual">

                ${createProductImage(product)}

                <button
                    class="wishlist recommendation-wishlist"
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
                        ${formatPrice(product)}
                    </span>

                    <span class="product-rating">

                        ${
                            product.rating !== null &&
                            product.rating !== undefined
                                ? `⭐ ${Number(
                                    product.rating
                                ).toFixed(1)}`
                                : "No rating"
                        }

                    </span>

                </div>


                <div class="product-actions">

                    <button
                        class="view-recommended-product"
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
   RECOMMENDATION EVENTS
========================================================= */

function attachRecommendationEvents(
    products
) {

    document
        .querySelectorAll(
            ".view-recommended-product"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const index =
                        Number(
                            button.dataset.index
                        );


                    const product =
                        products[index];


                    if (!product) {
                        return;
                    }


                    recordInteraction(
                        product.product_id,
                        "click"
                    );


                    openProductModal(
                        product
                    );
                }
            );
        });


    document
        .querySelectorAll(
            ".recommendation-wishlist"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                event => {

                    event.stopPropagation();


                    const card =
                        button.closest(
                            ".recommendation-card"
                        );


                    if (!card) {
                        return;
                    }


                    const index =
                        Number(
                            card.dataset
                                .recommendationIndex
                        );


                    const product =
                        products[index];


                    if (!product) {
                        return;
                    }


                    button.classList.toggle(
                        "active"
                    );


                    const isActive =
                        button.classList.contains(
                            "active"
                        );


                    button.textContent =
                        isActive
                            ? "♥"
                            : "♡";


                    if (isActive) {

                        recordInteraction(
                            product.product_id,
                            "wishlist"
                        );
                    }
                }
            );
        });
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


                searchProducts(
                    query
                );
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


                searchProducts(
                    query
                );
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
   RECOMMENDATION BUTTON
========================================================= */

if (recommendationButton) {

    recommendationButton.addEventListener(
        "click",
        getRecommendations
    );
}


if (userIdInput) {

    userIdInput.style.display =
        "none";
}


/* =========================================================
   SORT
========================================================= */

if (sortSelect) {

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
}


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
   PRODUCT MODAL CLOSE
========================================================= */

function closeProductModal() {

    productModal.classList.add(
        "hidden"
    );
}


if (closeModal) {

    closeModal.addEventListener(
        "click",
        closeProductModal
    );
}


if (modalOverlay) {

    modalOverlay.addEventListener(
        "click",
        closeProductModal
    );
}


document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape" &&
            productModal &&
            !productModal.classList.contains(
                "hidden"
            )
        ) {

            closeProductModal();
        }
    }
);


/* =========================================================
   AUTHENTICATION
========================================================= */


/* =========================================================
   OPEN LOGIN
========================================================= */

function openLoginModal() {

    if (!authModal) return;


    authModal.classList.remove(
        "hidden"
    );


    if (loginFormContainer) {

        loginFormContainer.classList.remove(
            "hidden"
        );
    }


    if (registerFormContainer) {

        registerFormContainer.classList.add(
            "hidden"
        );
    }


    if (loginStatus) {

        loginStatus.textContent = "";
    }


    if (registerStatus) {

        registerStatus.textContent = "";
    }
}


/* =========================================================
   OPEN REGISTER
========================================================= */

function openRegisterModal() {

    if (!authModal) return;


    authModal.classList.remove(
        "hidden"
    );


    if (registerFormContainer) {

        registerFormContainer.classList.remove(
            "hidden"
        );
    }


    if (loginFormContainer) {

        loginFormContainer.classList.add(
            "hidden"
        );
    }


    if (loginStatus) {

        loginStatus.textContent = "";
    }


    if (registerStatus) {

        registerStatus.textContent = "";
    }
}


/* =========================================================
   CLOSE AUTH MODAL
========================================================= */

function closeAuthenticationModal() {

    if (!authModal) return;


    authModal.classList.add(
        "hidden"
    );
}


/* =========================================================
   REGISTER USER
========================================================= */

async function registerUser(event) {

    event.preventDefault();


    if (!registerStatus) return;


    registerStatus.textContent =
        "Creating your account...";


    registerStatus.style.color =
        "";


    const username =
        registerUsername.value.trim();


    const email =
        registerEmail.value.trim();


    const password =
        registerPassword.value;


    if (
        !username ||
        !email ||
        !password
    ) {

        registerStatus.textContent =
            "Please fill in all fields.";

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/auth/register`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        username:
                            username,

                        email:
                            email,

                        password:
                            password

                    })
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch (jsonError) {

            console.warn(
                "Registration response was not JSON.",
                jsonError
            );
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Registration failed (${response.status})`
            );
        }


        registerStatus.textContent =
            "Account created successfully!";


        registerStatus.style.color =
            "#7ee787";


        setTimeout(
            () => {

                if (loginFormContainer) {

                    loginFormContainer.classList.remove(
                        "hidden"
                    );
                }


                if (registerFormContainer) {

                    registerFormContainer.classList.add(
                        "hidden"
                    );
                }


                if (loginEmail) {

                    loginEmail.value =
                        email;
                }


                registerStatus.textContent =
                    "";

            },
            1000
        );


    } catch (error) {

        console.error(
            "Registration error:",
            error
        );


        registerStatus.textContent =
            error.message ||
            "Unable to register.";

        registerStatus.style.color =
            "#ff6b81";
    }
}


/* =========================================================
   LOGIN USER
========================================================= */

async function loginUser(event) {

    event.preventDefault();


    if (!loginStatus) return;


    loginStatus.textContent =
        "Logging in...";


    loginStatus.style.color =
        "";


    const email =
        loginEmail.value.trim();


    const password =
        loginPassword.value;


    if (!email || !password) {

        loginStatus.textContent =
            "Please enter email and password.";

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        email:
                            email,

                        password:
                            password

                    })
                }
            );


        let data = {};


        try {

            data =
                await response.json();

        } catch (jsonError) {

            console.warn(
                "Login response was not JSON.",
                jsonError
            );
        }


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Login failed (${response.status})`
            );
        }


        localStorage.setItem(
            AUTH_TOKEN_KEY,
            data.access_token
        );


        const user =
            await getCurrentUser(
                data.access_token
            );


        localStorage.setItem(
            AUTH_USER_KEY,
            JSON.stringify(user)
        );


        updateAuthUI(
            user
        );


        loginStatus.textContent =
            "Login successful!";


        loginStatus.style.color =
            "#7ee787";


        setTimeout(
            () => {

                closeAuthenticationModal();


                if (loginForm) {

                    loginForm.reset();
                }

            },
            500
        );


    } catch (error) {

        console.error(
            "Login error:",
            error
        );


        loginStatus.textContent =
            error.message ||
            "Unable to login.";

        loginStatus.style.color =
            "#ff6b81";
    }
}
/* =========================================================
   GET CURRENT USER
========================================================= */

async function getCurrentUser(token) {

    const response =
        await fetch(
            `${API_URL}/auth/me`,
            {
                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


    let data = {};


    try {

        data =
            await response.json();

    } catch (jsonError) {

        console.warn(
            "User response was not JSON.",
            jsonError
        );
    }


    if (!response.ok) {

        throw new Error(
            data.detail ||
            `Unable to get user (${response.status})`
        );
    }


    return data;
}


/* =========================================================
   UPDATE AUTH UI
========================================================= */

function updateAuthUI(user) {

    if (
        !loginButton ||
        !registerButton ||
        !userMenu
    ) {

        return;
    }


    if (!user) {

        loginButton.classList.remove(
            "hidden"
        );


        registerButton.classList.remove(
            "hidden"
        );


        userMenu.classList.add(
            "hidden"
        );


        if (loggedInUsername) {

            loggedInUsername.textContent =
                "";
        }


        return;
    }


    loginButton.classList.add(
        "hidden"
    );


    registerButton.classList.add(
        "hidden"
    );


    userMenu.classList.remove(
        "hidden"
    );


    if (loggedInUsername) {

        loggedInUsername.textContent =
            `Hi, ${user.username}`;
    }
}


/* =========================================================
   LOGOUT
========================================================= */

function logoutUser() {

    localStorage.removeItem(
        AUTH_TOKEN_KEY
    );


    localStorage.removeItem(
        AUTH_USER_KEY
    );


    /*
     * Completely reload the website
     * so all user-specific state is reset.
     */

    window.location.reload();
}


/* =========================================================
   RESTORE AUTH SESSION
========================================================= */

async function restoreAuthSession() {

    const token =
        localStorage.getItem(
            AUTH_TOKEN_KEY
        );


    if (!token) {

        updateAuthUI(
            null
        );

        return;
    }


    try {

        const user =
            await getCurrentUser(
                token
            );


        localStorage.setItem(
            AUTH_USER_KEY,
            JSON.stringify(user)
        );


        updateAuthUI(
            user
        );


    } catch (error) {

        console.log(
            "Session expired or invalid."
        );


        localStorage.removeItem(
            AUTH_TOKEN_KEY
        );


        localStorage.removeItem(
            AUTH_USER_KEY
        );


        updateAuthUI(
            null
        );
    }
}


/* =========================================================
   AUTH EVENT LISTENERS
========================================================= */

if (loginButton) {

    loginButton.addEventListener(
        "click",
        openLoginModal
    );
}


if (registerButton) {

    registerButton.addEventListener(
        "click",
        openRegisterModal
    );
}


if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        logoutUser
    );
}


if (closeAuthModal) {

    closeAuthModal.addEventListener(
        "click",
        closeAuthenticationModal
    );
}


if (authModalOverlay) {

    authModalOverlay.addEventListener(
        "click",
        closeAuthenticationModal
    );
}


if (showRegisterButton) {

    showRegisterButton.addEventListener(
        "click",
        openRegisterModal
    );
}


if (showLoginButton) {

    showLoginButton.addEventListener(
        "click",
        openLoginModal
    );
}


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        loginUser
    );
}


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        registerUser
    );
}


/* =========================================================
   AUTH ESCAPE KEY
========================================================= */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape" &&
            authModal &&
            !authModal.classList.contains(
                "hidden"
            )
        ) {

            closeAuthenticationModal();
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
        value.includes("audio") ||
        value.includes("earbud")
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


    return "🛍️";
}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


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


/* =========================================================
   ESCAPE ATTRIBUTE
========================================================= */

function escapeAttribute(value) {

    return escapeHtml(
        value
    );
}


/* =========================================================
   RESTORE SESSION ON PAGE LOAD
========================================================= */

restoreAuthSession();


/* =========================================================
   STARTUP LOG
========================================================= */

console.log(
    "✦ AI Shop — Premium frontend loaded"
);