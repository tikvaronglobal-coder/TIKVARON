import {NextRequest,NextResponse} from "next/server";
import {authorizePreview} from "./lib/preview-auth.mjs";
import {isProtectedPath} from "./lib/route-access.mjs";
export function middleware(request:NextRequest){
 if(!isProtectedPath(request.nextUrl.pathname)) return NextResponse.next();
 const decision=authorizePreview({password:process.env.TIKVARON_PREVIEW_PASSWORD??"",authorization:request.headers.get("authorization"),isProduction:process.env.NODE_ENV==="production"});
 if(decision==="configuration_error") return new NextResponse("Private operations unavailable: password is not configured.",{status:503});
 if(decision==="allow") return NextResponse.next();
 return new NextResponse("Authentication required",{status:401,headers:{"WWW-Authenticate":'Basic realm="TIKVARON Private Operations"'}});
}
export const config={matcher:["/((?!_next/static|_next/image|favicon.ico).*)"]};