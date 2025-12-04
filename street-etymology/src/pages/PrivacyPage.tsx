import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export function PrivacyPage() {
  return (
    <div className="min-h-screen bg-stone-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm mb-8">
          <Link to="/" className="text-stone-500 hover:text-stone-700">Home</Link>
          <ChevronRight className="w-4 h-4 text-stone-400" />
          <span className="text-stone-800 font-medium">Privacy Policy</span>
        </nav>

        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8 md:p-12">
          <h1 className="text-3xl font-serif font-bold text-stone-800 mb-2">
            Privacy Policy
          </h1>
          <p className="text-stone-600 mb-8">
            Last updated: December 2024
          </p>

          <div className="prose prose-stone max-w-none">
            <h2>1. Introduction</h2>
            <p>
              Street Etymology UK ("we", "us", or "our") is committed to protecting your 
              privacy. This Privacy Policy explains how we collect, use, disclose, and 
              safeguard your information when you visit our website and use our services.
            </p>

            <h2>2. Information We Collect</h2>
            <h3>2.1 Information You Provide</h3>
            <p>We may collect information you provide directly, including:</p>
            <ul>
              <li><strong>Account Information:</strong> Email address, name (optional), and password when you create an account</li>
              <li><strong>Contributions:</strong> Etymology suggestions and sources you submit</li>
              <li><strong>Communications:</strong> Information in messages you send to us</li>
              <li><strong>Newsletter Subscription:</strong> Email address if you subscribe to our newsletter</li>
            </ul>

            <h3>2.2 Automatically Collected Information</h3>
            <p>When you access our website, we may automatically collect:</p>
            <ul>
              <li>Browser type and version</li>
              <li>Operating system</li>
              <li>IP address</li>
              <li>Pages visited and time spent</li>
              <li>Referring website</li>
            </ul>

            <h2>3. How We Use Your Information</h2>
            <p>We use collected information to:</p>
            <ul>
              <li>Provide, maintain, and improve our services</li>
              <li>Process and display your contributions</li>
              <li>Communicate with you about your account or contributions</li>
              <li>Send newsletters if you have opted in</li>
              <li>Analyse usage patterns to improve user experience</li>
              <li>Prevent fraud and ensure security</li>
            </ul>

            <h2>4. Data Storage and Security</h2>
            <p>
              We use Supabase, a secure cloud-based platform, to store your data. 
              All data is encrypted in transit using TLS and at rest. We implement 
              appropriate technical and organisational measures to protect your 
              personal information against unauthorised access, alteration, or destruction.
            </p>

            <h2>5. Data Sharing</h2>
            <p>We do not sell your personal information. We may share information with:</p>
            <ul>
              <li><strong>Service Providers:</strong> Third parties that help us operate our services (hosting, analytics)</li>
              <li><strong>Legal Requirements:</strong> When required by law or to protect our rights</li>
              <li><strong>Public Contributions:</strong> Etymology contributions you submit may be displayed publicly with your email anonymised</li>
            </ul>

            <h2>6. Your Rights</h2>
            <p>Under GDPR, you have the right to:</p>
            <ul>
              <li>Access your personal data</li>
              <li>Rectify inaccurate personal data</li>
              <li>Request erasure of your personal data</li>
              <li>Object to processing of your personal data</li>
              <li>Request restriction of processing</li>
              <li>Data portability</li>
              <li>Withdraw consent at any time</li>
            </ul>

            <h2>7. Cookies</h2>
            <p>
              We use essential cookies to enable core functionality such as authentication. 
              We may use analytics cookies to understand how visitors interact with our 
              website. You can control cookie preferences through your browser settings.
            </p>

            <h2>8. Third-Party Links</h2>
            <p>
              Our website may contain links to third-party websites. We are not responsible 
              for the privacy practices of these sites. We encourage you to review their 
              privacy policies.
            </p>

            <h2>9. Children's Privacy</h2>
            <p>
              Our services are not directed to individuals under 16. We do not knowingly 
              collect personal information from children. If we become aware that we have 
              collected personal information from a child, we will take steps to delete it.
            </p>

            <h2>10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of 
              any changes by posting the new policy on this page and updating the 
              "Last updated" date.
            </p>

            <h2>11. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or wish to exercise your 
              rights, please contact us at:
            </p>
            <p>
              <strong>Email:</strong> privacy@streetetymology.co.uk
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
