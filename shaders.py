vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in vec3 aNormal;
out vec2 TexCoord; out vec3 Normal; out vec3 FragPos;
uniform mat4 model; uniform mat4 view; uniform mat4 projection;
void main() {
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;  
    TexCoord = aTexCoord;
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;
in vec2 TexCoord; in vec3 Normal; in vec3 FragPos;
uniform sampler2D ourTexture; uniform vec3 lightPos; uniform vec3 objectColor; uniform float damageFlash;
void main() {
    // LUZ AMBIENTE MUCHO MAS FUERTE
    float ambientStrength = 0.6; 
    vec3 ambient = ambientStrength * objectColor;
    
    // LUZ DIFUSA
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * objectColor;
    
    vec4 texColor = texture(ourTexture, TexCoord);
    vec3 result = (ambient + diffuse) * texColor.rgb;
    
    // SIN NIEBLA POR AHORA PARA QUE VEAS BIEN
    
    // Flash de daño rojo
    result = mix(result, vec3(1.0, 0.0, 0.0), damageFlash);
    
    FragColor = vec4(result, 1.0);
}
"""