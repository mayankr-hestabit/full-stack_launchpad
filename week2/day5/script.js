const productContainer = document.getElementById("productContainer");
const searchInput = document.getElementById("searchInput");
const navLinks = document.querySelectorAll("nav a");

let products = [];
let currentProducts = [];

// ================= FETCH PRODUCTS =================

async function fetchProducts(url = "https://dummyjson.com/products") {

    try {

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Failed to fetch products");
        }

        const data = await response.json();

        products = data.products;
        currentProducts = [...products];

        renderProducts(currentProducts);
        showStats(currentProducts);

    }

    catch (error) {

        productContainer.innerHTML = `
            <h2 style="grid-column:1/-1;text-align:center;color:red;">
                ${error.message}
            </h2>
        `;

        console.log(error);

    }

}

// ================= RENDER PRODUCTS =================

function renderProducts(productList) {

    if (productList.length === 0) {

        productContainer.innerHTML = `
            <h2 style="grid-column:1/-1;text-align:center;">
                No Products Found
            </h2>
        `;

        return;

    }

    productContainer.innerHTML = productList.map((product, index) => {

        let badge = "";

        if (index % 3 === 0) {

            badge = `<span class="badge sale">SALE</span>`;

        }

        else if (index % 3 === 1) {

            badge = `<span class="badge new">NEW</span>`;

        }

        else {

            badge = `<span class="badge stock">OUT OF STOCK</span>`;

        }

        let stars = "";

        for (let i = 1; i <= 5; i++) {

            if (i <= Math.round(product.rating)) {

                stars += `<i class="fas fa-star"></i>`;

            }

            else {

                stars += `<i class="far fa-star"></i>`;

            }

        }

        return `

        <div class="card">

            <div class="image-box">

                ${badge}

                <img src="${product.thumbnail}" alt="${product.title}">

            </div>

            <div class="content">

                <h3>${product.title}</h3>

                <p class="category">${product.category}</p>

                <div class="rating">
                    ${stars}
                </div>

                <div class="price">
                    $${product.price}
                </div>

            </div>

        </div>

        `;

    }).join("");

}

// ================= REDUCE =================

function showStats(productList) {

    const averageRating = productList.reduce((sum, product) => {

        return sum + product.rating;

    }, 0) / productList.length;

    console.log("Average Rating:", averageRating.toFixed(2));

}

// Debounce function
function debounce(callback, delay) {

    let timer;

    return function (...args) {

        clearTimeout(timer);

        timer = setTimeout(() => {

            callback.apply(this, args);

        }, delay);

    };

}

// ================= SEARCH =================

const searchProducts = debounce(function () {

    const searchValue = this.value.toLowerCase();

    currentProducts = products.filter(product =>

        product.title.toLowerCase().includes(searchValue)

    );

    renderProducts(currentProducts);

    showStats(currentProducts);

}, 300);

searchInput.addEventListener("input", searchProducts);

// ================= CATEGORY FILTER =================

const categoryMap = {

    womens: "womens-dresses",
    mens: "mens-shirts",
    tops: "tops",
    beauty: "beauty",
    fragrances: "fragrances"

};

navLinks.forEach(link => {

    link.addEventListener("click", async function (e) {

        e.preventDefault();

        // Active navbar
        navLinks.forEach(item => item.classList.remove("active"));
        this.classList.add("active");

        // Clear search
        searchInput.value = "";

        const category = this.dataset.category;

        if (category === "all") {

            fetchProducts();
            return;

        }

        const apiCategory = categoryMap[category];

        if (!apiCategory) return;

        try {

            const response = await fetch(
                `https://dummyjson.com/products/category/${apiCategory}`
            );

            if (!response.ok) {
                throw new Error("Category not found");
            }

            const data = await response.json();

            products = data.products;
            currentProducts = [...products];

            renderProducts(currentProducts);

            showStats(currentProducts);

        }

        catch (error) {

            console.log(error);

            productContainer.innerHTML = `
                <h2 style="grid-column:1/-1;text-align:center;">
                    No Products Found
                </h2>
            `;

        }

    });

});

// ================= START =================

fetchProducts();