// Enhanced Fashion Knowledge Base from Datasets

const fashionDatabase = {
    // Clothing types from Fashion MNIST and DeepFashion2
    clothingTypes: {
        tops: [
            'T-shirt', 'Shirt', 'Blouse', 'Top', 'Sweater', 'Pullover', 'Hoodie',
            'Tank top', 'Crop top', 'Tunic', 'Cardigan', 'Jacket', 'Blazer',
            'Coat', 'Vest', 'Kurta', 'Anarkali top'
        ],
        bottoms: [
            'Trouser', 'Pants', 'Jeans', 'Skirt', 'Shorts', 'Leggings',
            'Palazzo', 'Culottes', 'Salwar', 'Dhoti pants'
        ],
        dresses: [
            'Dress', 'Gown', 'Midi dress', 'Maxi dress', 'Mini dress',
            'Bodycon dress', 'A-line dress', 'Shift dress', 'Wrap dress',
            'Off-shoulder dress', 'One-shoulder dress', 'Anarkali suit',
            'Saree', 'Lehenga', 'Salwar kameez'
        ],
        outerwear: [
            'Coat', 'Jacket', 'Blazer', 'Cardigan', 'Shawl', 'Cape'
        ],
        accessories: [
            'Bag', 'Sandal', 'Sneaker', 'Ankle boot', 'Belt', 'Scarf',
            'Hat', 'Dupatta'
        ]
    },

    // Color recommendations from body metrics dataset
    colorPairings: {
        // Skin tone based recommendations
        fair: {
            bestColors: ['navy', 'burgundy', 'emerald', 'royal blue', 'deep purple', 'black'],
            avoidColors: ['pale yellow', 'beige', 'light pastels']
        },
        medium: {
            bestColors: ['coral', 'teal', 'olive', 'mustard', 'burnt orange', 'wine red'],
            avoidColors: ['neon colors', 'very pale shades']
        },
        olive: {
            bestColors: ['earth tones', 'warm reds', 'golden yellow', 'forest green', 'rust'],
            avoidColors: ['orange', 'bright yellow']
        },
        dark: {
            bestColors: ['bright white', 'hot pink', 'electric blue', 'lime green', 'gold', 'silver'],
            avoidColors: ['brown', 'dark gray', 'muddy colors']
        }
    },

    // Pattern and style combinations
    patterns: {
        floral: {
            pairsWith: ['solid colors', 'stripes (thin)', 'denim'],
            occasions: ['casual', 'brunch', 'garden party', 'spring events'],
            bodyTypes: ['all', 'especially flattering for hourglass and pear']
        },
        stripes: {
            pairsWith: ['solid colors', 'denim', 'leather'],
            occasions: ['casual', 'office', 'smart casual'],
            bodyTypes: ['vertical stripes for all', 'horizontal for rectangle body']
        },
        polkaDots: {
            pairsWith: ['solid colors', 'denim'],
            occasions: ['retro events', 'casual outings', 'parties'],
            bodyTypes: ['all body types']
        },
        checkered: {
            pairsWith: ['solid colors', 'denim', 'black/white basics'],
            occasions: ['casual', 'office', 'outdoor events'],
            bodyTypes: ['all body types']
        },
        sequins: {
            pairsWith: ['solid colors', 'minimal accessories'],
            occasions: ['parties', 'evening events', 'celebrations'],
            bodyTypes: ['all body types', 'creates glamorous look']
        },
        embroidery: {
            pairsWith: ['solid colors', 'simple bottoms'],
            occasions: ['festive', 'weddings', 'cultural events'],
            bodyTypes: ['all body types']
        }
    },

    // Indian ethnic wear from women fashion dataset
    ethnicWear: {
        anarkali: {
            description: 'Long, flowing dress with fitted bodice',
            occasions: ['weddings', 'festivals', 'formal events'],
            styling: 'Pair with churidar or palazzo, add statement earrings',
            bodyTypes: ['hourglass', 'pear', 'apple - empire waist style']
        },
        saree: {
            description: 'Traditional draped garment',
            occasions: ['weddings', 'formal events', 'cultural celebrations'],
            styling: 'Choose blouse style based on body type, add jewelry',
            bodyTypes: ['all body types with right draping style']
        },
        salwarKameez: {
            description: 'Tunic with pants and dupatta',
            occasions: ['casual', 'office', 'festivals', 'daily wear'],
            styling: 'Straight cut for formal, A-line for casual',
            bodyTypes: ['all body types']
        },
        lehenga: {
            description: 'Long skirt with blouse and dupatta',
            occasions: ['weddings', 'grand celebrations'],
            styling: 'Crop top style blouse for modern look',
            bodyTypes: ['hourglass', 'pear', 'rectangle']
        }
    },

    // Western wear styles from women fashion dataset
    westernWear: {
        bodycon: {
            description: 'Form-fitting dress',
            occasions: ['parties', 'night out', 'cocktail events'],
            styling: 'Minimal accessories, statement heels',
            bodyTypes: ['hourglass', 'athletic']
        },
        aLine: {
            description: 'Fitted at top, flares at bottom',
            occasions: ['office', 'casual', 'semi-formal'],
            styling: 'Belt to define waist, versatile styling',
            bodyTypes: ['all body types', 'especially pear and apple']
        },
        offShoulder: {
            description: 'Shoulders exposed, elegant neckline',
            occasions: ['parties', 'dates', 'summer events'],
            styling: 'Statement earrings, avoid necklaces',
            bodyTypes: ['all body types', 'balances inverted triangle']
        },
        wrap: {
            description: 'Wraps around body, ties at waist',
            occasions: ['office', 'brunch', 'versatile'],
            styling: 'Defines waist, adjustable fit',
            bodyTypes: ['all body types', 'especially flattering for hourglass']
        },
        jumpsuit: {
            description: 'One-piece with pants',
            occasions: ['casual', 'parties', 'modern events'],
            styling: 'Belt at waist, statement accessories',
            bodyTypes: ['hourglass', 'rectangle', 'inverted triangle']
        }
    },

    // Fabric recommendations
    fabrics: {
        summer: ['cotton', 'linen', 'chiffon', 'georgette', 'silk'],
        winter: ['wool', 'velvet', 'knit', 'fleece', 'leather'],
        formal: ['silk', 'satin', 'velvet', 'brocade', 'taffeta'],
        casual: ['cotton', 'denim', 'jersey', 'linen']
    },

    // Occasion-based recommendations
    occasions: {
        wedding: {
            colors: ['red', 'maroon', 'gold', 'royal blue', 'emerald', 'pink'],
            styles: ['anarkali', 'lehenga', 'saree', 'gown', 'sharara'],
            accessories: ['statement jewelry', 'clutch', 'heels']
        },
        office: {
            colors: ['navy', 'black', 'gray', 'white', 'beige', 'pastels'],
            styles: ['blazer', 'trousers', 'pencil skirt', 'shirt', 'formal dress'],
            accessories: ['minimal jewelry', 'structured bag', 'closed-toe shoes']
        },
        party: {
            colors: ['black', 'red', 'gold', 'silver', 'sequins', 'metallics'],
            styles: ['bodycon', 'cocktail dress', 'jumpsuit', 'sequined outfit'],
            accessories: ['statement jewelry', 'clutch', 'heels']
        },
        casual: {
            colors: ['any comfortable colors', 'denim', 'pastels', 'prints'],
            styles: ['jeans', 't-shirt', 'casual dress', 'shorts', 'sneakers'],
            accessories: ['crossbody bag', 'sneakers', 'minimal jewelry']
        },
        festival: {
            colors: ['bright colors', 'traditional colors', 'gold accents'],
            styles: ['ethnic wear', 'traditional outfits', 'embroidered pieces'],
            accessories: ['traditional jewelry', 'ethnic footwear', 'dupatta']
        }
    },

    // Color psychology and meanings
    colorMeanings: {
        red: 'Power, passion, confidence, bold',
        blue: 'Trust, calm, professional, stable',
        black: 'Elegant, sophisticated, timeless, slimming',
        white: 'Pure, clean, fresh, versatile',
        yellow: 'Happy, energetic, optimistic, cheerful',
        green: 'Natural, balanced, refreshing, growth',
        purple: 'Luxury, creative, royal, mysterious',
        pink: 'Feminine, romantic, soft, playful',
        orange: 'Energetic, warm, friendly, vibrant',
        brown: 'Earthy, reliable, comfortable, natural',
        gray: 'Neutral, sophisticated, modern, balanced'
    }
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = fashionDatabase;
}
