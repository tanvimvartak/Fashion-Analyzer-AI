// Fashion MNIST Dataset Integration
// Dataset: Fashion 1 folder contains Fashion-MNIST dataset
// 70,000 grayscale images (28x28 pixels) of 10 fashion categories

const fashionMNIST = {
    // Label mapping from Fashion-MNIST dataset
    labels: {
        0: 'T-shirt/top',
        1: 'Trouser',
        2: 'Pullover',
        3: 'Dress',
        4: 'Coat',
        5: 'Sandal',
        6: 'Shirt',
        7: 'Sneaker',
        8: 'Bag',
        9: 'Ankle boot'
    },

    // Detailed category information
    categories: {
        'T-shirt/top': {
            type: 'top',
            description: 'Casual short-sleeved shirt',
            occasions: ['casual', 'everyday', 'sports'],
            pairsWith: ['jeans', 'shorts', 'skirts', 'trousers'],
            bodyTypes: ['all'],
            styling: 'Versatile basic piece, can be dressed up or down'
        },
        'Trouser': {
            type: 'bottom',
            description: 'Formal or casual pants',
            occasions: ['office', 'formal', 'casual'],
            pairsWith: ['shirts', 'blouses', 'sweaters', 't-shirts'],
            bodyTypes: ['all', 'straight-leg flatters rectangle body'],
            styling: 'Choose fit based on occasion - slim for formal, relaxed for casual'
        },
        'Pullover': {
            type: 'top',
            description: 'Knitted sweater worn over other clothes',
            occasions: ['casual', 'winter', 'layering'],
            pairsWith: ['jeans', 'trousers', 'skirts'],
            bodyTypes: ['all', 'fitted styles for hourglass'],
            styling: 'Perfect for layering, choose V-neck to elongate torso'
        },
        'Dress': {
            type: 'one-piece',
            description: 'One-piece garment for women',
            occasions: ['casual', 'formal', 'party', 'office'],
            pairsWith: ['jackets', 'cardigans', 'belts'],
            bodyTypes: ['all', 'style varies by body type'],
            styling: 'Choose silhouette based on body type - A-line for pear, wrap for hourglass'
        },
        'Coat': {
            type: 'outerwear',
            description: 'Outer garment for warmth or fashion',
            occasions: ['winter', 'formal', 'outdoor'],
            pairsWith: ['any outfit as outer layer'],
            bodyTypes: ['all', 'fitted for hourglass, structured for rectangle'],
            styling: 'Should complement outfit underneath, not overpower it'
        },
        'Sandal': {
            type: 'footwear',
            description: 'Open-toed casual footwear',
            occasions: ['casual', 'summer', 'beach', 'outdoor'],
            pairsWith: ['shorts', 'dresses', 'casual pants', 'skirts'],
            bodyTypes: ['all'],
            styling: 'Great for warm weather, choose heeled sandals for dressier occasions'
        },
        'Shirt': {
            type: 'top',
            description: 'Button-up formal or casual top',
            occasions: ['office', 'formal', 'smart casual'],
            pairsWith: ['trousers', 'skirts', 'jeans'],
            bodyTypes: ['all', 'fitted for hourglass, loose for apple'],
            styling: 'Tuck in for formal look, leave untucked for casual'
        },
        'Sneaker': {
            type: 'footwear',
            description: 'Athletic or casual sports shoe',
            occasions: ['casual', 'sports', 'everyday', 'athleisure'],
            pairsWith: ['jeans', 'joggers', 'shorts', 'casual dresses'],
            bodyTypes: ['all'],
            styling: 'Comfortable and trendy, works with athleisure and casual outfits'
        },
        'Bag': {
            type: 'accessory',
            description: 'Handbag or purse',
            occasions: ['all occasions'],
            pairsWith: ['any outfit'],
            bodyTypes: ['all', 'size should balance body proportions'],
            styling: 'Choose size and style based on occasion - clutch for formal, tote for casual'
        },
        'Ankle boot': {
            type: 'footwear',
            description: 'Boot that covers ankle',
            occasions: ['casual', 'fall', 'winter', 'smart casual'],
            pairsWith: ['jeans', 'dresses', 'skirts', 'trousers'],
            bodyTypes: ['all', 'heeled boots elongate legs'],
            styling: 'Versatile for multiple seasons, pairs well with both casual and dressy outfits'
        }
    },

    // Styling combinations from Fashion-MNIST categories
    outfitCombinations: [
        {
            name: 'Casual Everyday',
            items: ['T-shirt/top', 'Trouser', 'Sneaker', 'Bag'],
            occasion: 'casual, everyday wear',
            season: 'all seasons'
        },
        {
            name: 'Smart Casual',
            items: ['Shirt', 'Trouser', 'Ankle boot', 'Bag'],
            occasion: 'office, meetings, smart casual events',
            season: 'all seasons'
        },
        {
            name: 'Winter Casual',
            items: ['Pullover', 'Trouser', 'Ankle boot', 'Coat'],
            occasion: 'cold weather, casual outings',
            season: 'fall, winter'
        },
        {
            name: 'Summer Casual',
            items: ['T-shirt/top', 'Trouser', 'Sandal', 'Bag'],
            occasion: 'warm weather, casual',
            season: 'spring, summer'
        },
        {
            name: 'Dress Up',
            items: ['Dress', 'Ankle boot', 'Bag'],
            occasion: 'parties, dates, semi-formal',
            season: 'all seasons'
        },
        {
            name: 'Layered Look',
            items: ['Shirt', 'Pullover', 'Trouser', 'Sneaker'],
            occasion: 'casual, transitional weather',
            season: 'fall, spring'
        }
    ],

    // Get recommendations based on item type
    getRecommendations: function(itemType) {
        const category = this.categories[itemType];
        if (!category) return null;

        return {
            type: category.type,
            description: category.description,
            occasions: category.occasions,
            pairsWith: category.pairsWith,
            bodyTypes: category.bodyTypes,
            styling: category.styling
        };
    },

    // Get outfit suggestions
    getOutfitSuggestions: function(itemType) {
        return this.outfitCombinations.filter(combo => 
            combo.items.includes(itemType)
        );
    },

    // Identify item type from description
    identifyItem: function(description) {
        const lowerDesc = description.toLowerCase();
        
        for (const [label, name] of Object.entries(this.labels)) {
            if (lowerDesc.includes(name.toLowerCase())) {
                return {
                    label: parseInt(label),
                    name: name,
                    details: this.categories[name]
                };
            }
        }
        
        return null;
    }
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = fashionMNIST;
}
