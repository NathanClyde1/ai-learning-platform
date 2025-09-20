"""Comprehensive topic database for specific responses"""

TOPICS = {
    'react': {
        'beginner': "React is a JavaScript library created by Facebook in 2013. It helps build websites by breaking them into reusable pieces called components. Think of it like LEGO blocks - you create small pieces and combine them to build bigger things.",
        'intermediate': "React uses a virtual DOM and JSX syntax to efficiently update web interfaces. Components manage state through hooks like useState and useEffect. Popular tools include Create React App, Next.js, and React Router for building single-page applications.",
        'advanced': "React implements a reconciliation algorithm with fiber architecture for concurrent rendering. Advanced patterns include render props, higher-order components, context API, and custom hooks. Performance optimization uses React.memo, useMemo, and useCallback."
    },
    'javascript': {
        'beginner': "JavaScript is the programming language that makes websites interactive. Created by Brendan Eich in 1995, it runs in web browsers and lets you create animations, handle clicks, and update content without refreshing the page.",
        'intermediate': "JavaScript is an interpreted language with dynamic typing, prototypal inheritance, and first-class functions. ES6+ features include arrow functions, destructuring, modules, and async/await. Node.js enables server-side JavaScript development.",
        'advanced': "JavaScript uses an event loop with call stack, callback queue, and microtask queue. Advanced concepts include closures, hoisting, prototype chain, and execution contexts. V8 engine optimizations include JIT compilation and garbage collection."
    },
    'aws': {
        'beginner': "Amazon Web Services (AWS) is like renting computer power from Amazon instead of buying your own servers. Launched in 2006, it offers services like storage (S3), computing (EC2), and databases that you pay for as you use.",
        'intermediate': "AWS provides 200+ cloud services including compute (EC2, Lambda), storage (S3, EBS), databases (RDS, DynamoDB), and networking (VPC, CloudFront). Services are deployed across global regions and availability zones for reliability.",
        'advanced': "AWS architecture patterns include microservices with API Gateway, event-driven systems using EventBridge, and serverless computing with Lambda. Advanced services include EKS for Kubernetes, SageMaker for ML, and Well-Architected Framework principles."
    },
    'docker': {
        'beginner': "Docker is like a shipping container for software. Created by Solomon Hykes in 2013, it packages your application with everything it needs to run, so it works the same way on any computer - your laptop, servers, or the cloud.",
        'intermediate': "Docker uses containerization to isolate applications using Linux namespaces and cgroups. Key concepts include images, containers, Dockerfile for building, Docker Compose for multi-container apps, and registries like Docker Hub for sharing.",
        'advanced': "Docker implements container runtime using containerd and runc. Advanced features include multi-stage builds, BuildKit for improved performance, Docker Swarm for orchestration, and security scanning. Integration with Kubernetes via CRI."
    },
    'kubernetes': {
        'beginner': "Kubernetes (K8s) is like an orchestra conductor for containers. Created by Google in 2014, it automatically manages, scales, and heals containerized applications across multiple computers, ensuring they keep running smoothly.",
        'intermediate': "Kubernetes orchestrates containers using pods, services, deployments, and ingress controllers. Key features include auto-scaling, rolling updates, service discovery, and persistent storage. kubectl is the command-line tool for cluster management.",
        'advanced': "Kubernetes uses etcd for cluster state, kube-scheduler for pod placement, and kubelet for node management. Advanced concepts include custom resources, operators, admission controllers, and network policies using CNI plugins like Calico."
    }
}

def get_topic_response(topic, level):
    """Get specific response for a topic and level"""
    topic_key = topic.lower().strip()
    
    # Direct match
    if topic_key in TOPICS:
        return TOPICS[topic_key].get(level, TOPICS[topic_key]['beginner'])
    
    # Partial match
    for key in TOPICS:
        if key in topic_key or topic_key in key:
            return TOPICS[key].get(level, TOPICS[key]['beginner'])
    
    return None