document.addEventListener('DOMContentLoaded', () => {
    // Handle recipe search form submission
    document.getElementById('ingredient-form').addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const ingredients = document.getElementById('ingredients').value.split(',').map(ingredient => ingredient.trim());
        
        try {
            const response = await fetch('/filter_recipes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ingredients }),
            });
            
            const data = await response.json();
            const recipesContainer = document.getElementById('recipes-container');
            
            if (data.error) {
                recipesContainer.innerHTML = `<p>${data.error}</p>`;
            } else {
                const recipes = data.map(recipe => `
                    <div class="recipe">
                        <h3>${recipe.name}</h3>
                        <img src="${recipe.image}" alt="${recipe.name}" style="max-width: 200px; height: auto;">
                        <p>${recipe.description}</p>
                        <a href="${recipe.url}" target="_blank">View Recipe</a>
                    </div>
                `).join('');
                recipesContainer.innerHTML = recipes;
            }
        } catch (error) {
            console.error('Error fetching recipes:', error);
            document.getElementById('recipes-container').innerHTML = 'Failed to fetch recipes.';
        }
    });

    // Handle substitute ingredient request
    document.getElementById('get-substitute').addEventListener('click', async function(event) {
        event.preventDefault();

        const ingredient = document.getElementById('substitute-ingredient').value.trim();
        
        if (!ingredient) {
            document.getElementById('substitute-container').innerHTML = 'Please enter an ingredient.';
            return;
        }
        
        try {
            const response = await fetch('/substitute_ingredient', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ingredient }),
            });
            
            const data = await response.json();
            const substituteContainer = document.getElementById('substitute-container');
            
            if (data.length === 0) {
                substituteContainer.innerHTML = 'No substitutes found.';
            } else {
                const substitutes = data.join(', ');
                substituteContainer.innerHTML = `Substitutes: ${substitutes}`;
            }
        } catch (error) {
            console.error('Error fetching substitutes:', error);
            document.getElementById('substitute-container').innerHTML = 'Failed to fetch substitutes.';
        }
    });
});
